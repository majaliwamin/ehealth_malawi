import os
import asyncio
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from .core.config import settings
from .core.database import init_db, close_db
from .core.redis_service import get_redis, close_redis
from .api.v1.router import router as api_router
from .ws.dashboard_ws import router as ws_router, broadcast_dashboard_updates


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await get_redis()
    broadcast_task = asyncio.create_task(broadcast_dashboard_updates())
    yield
    broadcast_task.cancel()
    try:
        await broadcast_task
    except asyncio.CancelledError:
        pass
    await close_redis()
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="eHealth Malawi - Modular AI-Powered Digital Health Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(ws_router)


FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")


@app.get("/")
async def root():
    index = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "operational",
        "mode": "offline" if settings.OFFLINE_MODE else "online",
        "database": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
        "redis_configured": bool(settings.REDIS_URL),
        "sync_configured": bool(settings.SYNC_SERVER_URL),
        "modules": [
            "patient_registration",
            "appointment_queue",
            "outpatient_clinical",
            "inpatient_ward",
            "emergency_triage",
            "nursing_documentation",
            "vital_signs",
            "physician_documentation",
            "provider_workflow",
            "laboratory",
            "pharmacy_prescribing",
            "dialysis_ckd",
            "critical_care",
            "inventory_supplies",
            "clinical_governance",
            "multidisciplinary",
            "health_information_exchange",
            "billing_payments",
            "administration_audit",
        ],
    }
