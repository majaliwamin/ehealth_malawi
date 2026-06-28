from fastapi import APIRouter
from .endpoints import patients, clinical, appointments, laboratory, pharmacy, auth, dashboard, billing, info_center, notifications, sync

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(patients.router)
router.include_router(clinical.router)
router.include_router(appointments.router)
router.include_router(laboratory.router)
router.include_router(pharmacy.router)
router.include_router(dashboard.router)
router.include_router(billing.router)
router.include_router(info_center.router)
router.include_router(notifications.router)
router.include_router(sync.router)
