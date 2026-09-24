import sqlite3
import psutil
import time
import threading
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

THRESHOLDS = {"cpu": 75, "memory": 75, "disk": 90}
_last_net = psutil.net_io_counters()

def get_db():
    conn = sqlite3.connect("metrics.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            timestamp TEXT, cpu REAL, memory REAL, disk REAL,
            net_sent REAL, net_recv REAL, processes INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            timestamp TEXT, metric TEXT, value REAL, message TEXT
        )
    """)
    return conn

def collect_metrics():
    global _last_net
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    processes = len(psutil.pids())

    current_net = psutil.net_io_counters()
    net_sent = current_net.bytes_sent - _last_net.bytes_sent
    net_recv = current_net.bytes_recv - _last_net.bytes_recv
    _last_net = current_net

    timestamp = datetime.utcnow().isoformat()

    conn = get_db()
    conn.execute(
        "INSERT INTO metrics VALUES (?, ?, ?, ?, ?, ?, ?)",
        (timestamp, cpu, memory, disk, net_sent, net_recv, processes)
    )

    for metric, value in [("cpu", cpu), ("memory", memory), ("disk", disk)]:
        if value > THRESHOLDS[metric]:
            message = f"{metric.upper()} is high: {value:.1f}%"
            conn.execute(
                "INSERT INTO alerts VALUES (?, ?, ?, ?)",
                (timestamp, metric, value, message)
            )
            print(f"ALERT: {message}")

    conn.commit()
    conn.close()
    print(f"Collected: {timestamp} CPU={cpu}% MEM={memory}% DISK={disk}%")

def burn_cpu(duration):
    end = time.time() + duration
    while time.time() < end:
        pass

def burn_memory(duration, size_mb=3000):
    block = bytearray(size_mb * 1024 * 1024)
    time.sleep(duration)
    del block

scheduler = BackgroundScheduler()
scheduler.add_job(collect_metrics, "interval", seconds=15)
scheduler.start()
collect_metrics()

@app.get("/api/metrics")
def get_metrics():
    conn = get_db()
    rows = conn.execute(
        "SELECT timestamp, cpu, memory, disk FROM metrics ORDER BY timestamp DESC LIMIT 100"
    ).fetchall()
    conn.close()
    rows.reverse()
    return JSONResponse([
        {"timestamp": r[0], "cpu": r[1], "memory": r[2], "disk": r[3]} for r in rows
    ])

@app.get("/api/status")
def get_status():
    conn = get_db()
    row = conn.execute(
        "SELECT cpu, memory, disk, processes FROM metrics ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    conn.close()
    uptime_seconds = time.time() - psutil.boot_time()
    uptime = str(timedelta(seconds=int(uptime_seconds)))
    if not row:
        return JSONResponse({"status": "collecting"})
    cpu, memory, disk, processes = row
    healthy = cpu < THRESHOLDS["cpu"] and memory < THRESHOLDS["memory"] and disk < THRESHOLDS["disk"]
    return JSONResponse({
        "status": "healthy" if healthy else "warning",
        "cpu": cpu, "memory": memory, "disk": disk,
        "processes": processes, "uptime": uptime
    })

@app.get("/api/alerts")
def get_alerts():
    conn = get_db()
    rows = conn.execute(
        "SELECT timestamp, message FROM alerts ORDER BY timestamp DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return JSONResponse([{"timestamp": r[0], "message": r[1]} for r in rows])

@app.post("/api/stress/cpu")
def start_cpu_stress():
    threading.Thread(target=burn_cpu, args=(20,), daemon=True).start()
    return JSONResponse({"status": "started", "type": "cpu", "duration": 20})

@app.post("/api/stress/memory")
def start_memory_stress():
    threading.Thread(target=burn_memory, args=(20,), daemon=True).start()
    return JSONResponse({"status": "started", "type": "memory", "duration": 20})

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
    <head>
        <title>Server Performance Metrics</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
        <style>
            body { background: #0f1117; color: #e6e6e6; font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; }
            h2 { font-weight: 600; }
            .cards { display: flex; gap: 16px; flex-wrap: wrap; margin: 20px 0; }
            .card { background: #1a1d27; border-radius: 10px; padding: 16px 20px; flex: 1; min-width: 120px; }
            .card .label { font-size: 12px; color: #9a9ba5; text-transform: uppercase; }
            .card .value { font-size: 28px; font-weight: 700; margin-top: 4px; }
            .status-banner { padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; font-weight: 600; }
            .healthy { background: #133a2a; color: #4ade80; }
            .warning { background: #3a1f13; color: #fb923c; }
            .buttons { display: flex; gap: 12px; }
            button { background: #6366f1; color: white; border: none; padding: 10px 18px; border-radius: 8px; cursor: pointer; font-size: 14px; }
            button:hover { background: #4f46e5; }
            .alerts { margin-top: 20px; font-size: 13px; color: #9a9ba5; }
            .alerts div { padding: 6px 0; border-bottom: 1px solid #232633; }
        </style>
    </head>
    <body>
        <h2>Server Performance Metrics</h2>
        <div id="banner" class="status-banner healthy">Checking status...</div>
        <div class="cards" id="cards"></div>
        <div class="buttons">
            <button onclick="stress('cpu')">Simulate CPU load</button>
            <button onclick="stress('memory')">Simulate memory load</button>
        </div>
        <canvas id="chart" style="margin-top: 24px;"></canvas>
        <div class="alerts"><strong>Recent alerts</strong><div id="alertList"></div></div>

        <script>
            let chart;
            async function loadStatus() {
                const res = await fetch('/api/status');
                const d = await res.json();
                if (d.status === 'collecting') return;
                const banner = document.getElementById('banner');
                banner.className = 'status-banner ' + (d.status === 'healthy' ? 'healthy' : 'warning');
                banner.textContent = d.status === 'healthy' ? 'Systems operational' : 'Systems under load';
                document.getElementById('cards').innerHTML = `
                    <div class="card"><div class="label">CPU</div><div class="value">${d.cpu.toFixed(1)}%</div></div>
                    <div class="card"><div class="label">Memory</div><div class="value">${d.memory.toFixed(1)}%</div></div>
                    <div class="card"><div class="label">Disk</div><div class="value">${d.disk.toFixed(1)}%</div></div>
                    <div class="card"><div class="label">Processes</div><div class="value">${d.processes}</div></div>
                    <div class="card"><div class="label">Uptime</div><div class="value" style="font-size:18px;">${d.uptime}</div></div>
                `;
            }

            async function loadChart() {
                const res = await fetch('/api/metrics');
                const data = await res.json();
                const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
                const cpu = data.map(d => d.cpu);
                const memory = data.map(d => d.memory);
                const disk = data.map(d => d.disk);

                if (chart) { chart.destroy(); }
                chart = new Chart(document.getElementById('chart'), {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [
                            { label: 'CPU %', data: cpu, borderColor: '#f87171', fill: false, tension: 0.3 },
                            { label: 'Memory %', data: memory, borderColor: '#60a5fa', fill: false, tension: 0.3 },
                            { label: 'Disk %', data: disk, borderColor: '#4ade80', fill: false, tension: 0.3 }
                        ]
                    },
                    options: {
                        scales: {
                            y: { min: 0, max: 100, grid: { color: '#232633' }, ticks: { color: '#9a9ba5' } },
                            x: { grid: { color: '#232633' }, ticks: { color: '#9a9ba5' } }
                        },
                        plugins: { legend: { labels: { color: '#e6e6e6' } } }
                    }
                });
            }

            async function loadAlerts() {
                const res = await fetch('/api/alerts');
                const data = await res.json();
                document.getElementById('alertList').innerHTML = data.length
                    ? data.map(a => `<div>${new Date(a.timestamp).toLocaleTimeString()} \u2014 ${a.message}</div>`).join('')
                    : '<div>No alerts recorded</div>';
            }

            async function stress(type) {
                await fetch('/api/stress/' + type, { method: 'POST' });
                alert('Simulated ' + type.toUpperCase() + ' load running for 20 seconds ');
            }

            function refreshAll() {
                loadStatus();
                loadChart();
                loadAlerts();
            }

            refreshAll();
            setInterval(refreshAll, 5000);
        </script>
    </body>
    </html>
    """
