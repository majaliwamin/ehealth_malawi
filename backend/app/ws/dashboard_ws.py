from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import AsyncSessionLocal
from ..core.security import decode_access_token
from .manager import manager
from ..api.v1.endpoints.dashboard import get_ops_center, get_ai_insights, get_disease_surveillance
import asyncio
from datetime import datetime

router = APIRouter()


@router.websocket("/api/v1/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket, token: str = Query(...)):
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)


async def broadcast_dashboard_updates():
    while True:
        try:
            async with AsyncSessionLocal() as db:
                ops = await get_ops_center(db, None)
                ds = await get_disease_surveillance(db, None)
                ai = await get_ai_insights(db, None)
                await manager.broadcast({
                    "type": "dashboard_update",
                    "ops_center": ops.model_dump(),
                    "disease_surveillance": ds.model_dump(),
                    "ai_insights": ai,
                    "timestamp": datetime.now().isoformat(),
                })
        except Exception:
            pass
        await asyncio.sleep(10)
