"""Small demo service deployed by the GitOps pipeline.

Endpoints:
  /         -> greeting + version
  /healthz  -> liveness probe
  /readyz   -> readiness probe
  /metrics  -> Prometheus metrics
"""
import os
import time

from flask import Flask, Response, g, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

APP_VERSION = os.getenv("APP_VERSION", "dev")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

app = Flask(__name__)

REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["path"]
)


@app.before_request
def _start_timer():
    g.start = time.perf_counter()


@app.after_request
def _record_metrics(response):
    if request.path != "/metrics":
        LATENCY.labels(request.path).observe(time.perf_counter() - g.start)
        REQUESTS.labels(request.method, request.path, str(response.status_code)).inc()
    return response


@app.get("/")
def index():
    return jsonify(
        message="Hello from the GitOps demo app",
        version=APP_VERSION,
        environment=ENVIRONMENT,
    )


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.get("/readyz")
def readyz():
    return jsonify(status="ready")


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
