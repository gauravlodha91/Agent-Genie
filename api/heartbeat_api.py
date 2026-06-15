from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/heartbeat")
async def heartbeat():
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat() + "Z"}
