from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.api.extract import router as extract_router

app = FastAPI(title="Contract Intelligence API")

app.include_router(ingest_router)
app.include_router(extract_router)
