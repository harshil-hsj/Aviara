from fastapi import FastAPI
from app.api.ingest import router as ingest_router

app = FastAPI(title="Contract Intelligence API")

app.include_router(ingest_router)
