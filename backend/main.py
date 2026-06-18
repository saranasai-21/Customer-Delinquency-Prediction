# backend/main.py

import os
import sys
import time

# Inject path logic for Vercel/local runs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Histogram

# Import Routers
from backend.api.routers import predict, model, agents, auth

# Define database engines on startup
from backend.database.models import Base, get_db_session_factory
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    if "VERCEL" in os.environ:
        DATABASE_URL = "sqlite:////tmp/predictions.db"
    else:
        DATABASE_URL = "sqlite:///./predictions.db"
session_factory = get_db_session_factory(DATABASE_URL)

app = FastAPI(
    title="Enterprise Customer Delinquency Risk API",
    description="Bank-grade Customer Delinquency Risk Prediction System.",
    version="2.0.0"
)

# CORS Policy configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics setup
REQUEST_COUNT = Counter("api_requests_total", "Total API Requests", ["method", "endpoint", "http_status"])
REQUEST_LATENCY = Histogram("api_request_duration_seconds", "API Request Latency", ["endpoint"])

# Prometheus ASGI Exporter mounted at /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Middleware for latency audits and Prometheus metrics tracking."""
    start_time = time.time()
    endpoint = request.url.path
    
    # Exclude metrics from latency checks
    if endpoint == "/metrics":
        return await call_next(request)
        
    response = await call_next(request)
    
    latency = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=response.status_code).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    
    return response

# Register API Routers
app.include_router(auth.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(model.router, prefix="/api")
app.include_router(agents.router, prefix="/api")

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database_connected": True
    }