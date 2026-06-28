import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ....core.config import settings
from ....core.database import get_async_session, async_engine
from ....middleware.auth import get_current_user
from ....models import User
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sync", tags=["Sync"])


class SyncPushRequest(BaseModel):
    table: str
    operation: str  # insert / update / delete
    row_id: Optional[int] = None
    data: dict


class SyncPullRequest(BaseModel):
    last_sync_at: Optional[str] = None
    tables: list[str] = []


async def _sync_headers():
    return {
        "X-Site-ID": settings.SYNC_SITE_ID,
        "X-API-Key": settings.SYNC_API_KEY,
        "Content-Type": "application/json",
    }


@router.post("/push")
async def push_changes(
    req: SyncPushRequest,
    current_user: User = Depends(get_current_user),
):
    if not settings.SYNC_SERVER_URL:
        raise HTTPException(status_code=400, detail="SYNC_SERVER_URL not configured")
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"{settings.SYNC_SERVER_URL}/api/sync/push",
                json=req.model_dump(),
                headers=await _sync_headers(),
            )
            if r.status_code == 200:
                return r.json()
            logger.error("Sync push failed: %s %s", r.status_code, r.text)
            raise HTTPException(status_code=r.status_code, detail="Sync push failed")
    except httpx.RequestError as e:
        logger.warning("Sync server unreachable: %s", e)
        raise HTTPException(status_code=502, detail=f"Sync server unreachable: {e}")


@router.post("/pull")
async def pull_changes(
    req: SyncPullRequest,
    current_user: User = Depends(get_current_user),
):
    if not settings.SYNC_SERVER_URL:
        raise HTTPException(status_code=400, detail="SYNC_SERVER_URL not configured")
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(
                f"{settings.SYNC_SERVER_URL}/api/sync/pull",
                json=req.model_dump(),
                headers=await _sync_headers(),
            )
            if r.status_code == 200:
                return r.json()
            logger.error("Sync pull failed: %s %s", r.status_code, r.text)
            raise HTTPException(status_code=r.status_code, detail="Sync pull failed")
    except httpx.RequestError as e:
        logger.warning("Sync server unreachable: %s", e)
        raise HTTPException(status_code=502, detail=f"Sync server unreachable: {e}")


@router.get("/status")
async def sync_status(
    current_user: User = Depends(get_current_user),
):
    return {
        "sync_server_url": settings.SYNC_SERVER_URL or "(not configured)",
        "site_id": settings.SYNC_SITE_ID,
        "api_key_configured": bool(settings.SYNC_API_KEY),
        "mode": "offline" if settings.OFFLINE_MODE else "online",
        "database": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
    }
