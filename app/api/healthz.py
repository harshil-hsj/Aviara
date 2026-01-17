from fastapi import APIRouter
from app.db.db import client as mongo_client

router = APIRouter()

@router.get("/healthz",summary="Return healtcheck status for Server and Database")
def healthz():
    try:
        mongo_client.admin.command("ping")
        db_status = "configured"
    except Exception:
        db_status = "down"

    return {
        "status": "ok",
        "db_configuration": db_status
    }