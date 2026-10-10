FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py database.py alerting.py .
ENV MONITOR_DB_PATH=/data/metrics.db
RUN mkdir -p /data
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
