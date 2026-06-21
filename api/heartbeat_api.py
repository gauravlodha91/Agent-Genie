from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/heartbeat")
async def heartbeat() -> dict[str, str]:
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat() + "Z"}
