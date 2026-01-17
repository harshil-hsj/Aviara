from datetime import datetime
from fastapi import APIRouter
import time

router = APIRouter()
SERVICE_START_TIME = time.time()

@router.get(
    "/metrics",
    summary="Service metrics"
)
def metrics():
    uptime = int(time.time() - SERVICE_START_TIME)
    uptime_hms = time.strftime("%H:%M:%S", time.gmtime(uptime))
    start_datetime = datetime.fromtimestamp(
        SERVICE_START_TIME
    ).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "start_time": start_datetime,
        "uptime": uptime_hms
    }