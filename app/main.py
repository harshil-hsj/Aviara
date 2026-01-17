from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.api.extract import router as extract_router
from app.api.ask import router as ask_router
from app.api.audit import router as audit_router
from app.api.stream import router as stream_router
from app.api.healthz import router as health_router
from app.api.metrics import router as metrics_router

app = FastAPI(title="Contract Intelligence API")

app.include_router(ingest_router)
app.include_router(extract_router)
app.include_router(ask_router)
app.include_router(audit_router)
app.include_router(stream_router)
app.include_router(health_router)
app.include_router(metrics_router)
