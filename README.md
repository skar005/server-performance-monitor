# Server Performance Monitor

Live server monitoring dashboard that collects CPU, memory, disk, network, and process metrics on a schedule, stores past data, raises alerts when thresholds crossed, and includes on-demand load simulation for testing. Built and deployed on a live cloud server (Oracle Cloud Infrastructure), automated testing and deployment via GitHub Actions.

## Function

- Collects system metrics every 15 seconds using a background scheduler
- Stores full readings in SQLite
- Automated flagging and logging alerts when CPU, memory, or disk usage cross set threshold
- Live dashboard with realtime chart, status widgets, and running alert log
- Built-in CPU and memory stress-test buttons to demonstrate the monitoring and alerting system reacting to real load on demand

## Why I built it

I wanted a project focused on observability, scheduled background processes, and responding to infrastructure states, to practice and demonstrate integration of multiple systems and optimise constraints.

## Programming architecture

The project contains several dedicated modules, allows editing and testing of individual modules separately.  Modules:

- `app.py` — orchestrates everything: runs the background scheduler, exposes the API endpoints, and runs dashboard
- `database.py` — owns all database logic (schema and connections)
- `alerting.py` —  threshold-checking, separate from the database and API
- `tests/` — a pytest suite covering the alerting logic, database layer, and API endpoints seperately

Allows editing and testing of individual modules separately.

## Tech stack

- **Backend:** Python, FastAPI, APScheduler
- **Metrics collection:** psutil
- **Storage:** SQLite
- **Frontend:** Vanilla JS + Chart.js (no framework)
- **Containerisation:** Docker
- **Testing:** pytest
- **CI/CD:** GitHub Actions — runs the test suite on every push, automatically deploys to the live server if tests succeed
- **Hosting:** Oracle Cloud Infrastructure (Ampere ARM VM, Ubuntu 24.04)

## Running locally

```bash
docker build -t monitor .
docker run -d -p 8080:80 monitor
```

Then visit `http://localhost:8080`.

## Running the tests

```bash
python -m pytest -v
```

## Potential improvements

- Swap metrics storage and dashboard with Prometheus + Grafana stack
- Thresholds are static values - consider thresholds for prolonged load or unexpected activity
- Automate data retention to condense database
