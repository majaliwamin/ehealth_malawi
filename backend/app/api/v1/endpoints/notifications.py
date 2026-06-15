from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ....core.database import get_async_session
from ....middleware.auth import get_current_user
from ....models import User, NotificationLog, NotificationStatus, NotificationChannel
from ....schemas.notification import SendNotificationRequest, WhatsAppOptinRequest
from ....services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/optin")
async def whatsapp_optin(
    data: WhatsAppOptinRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    number = data.whatsapp_number.strip()
    if not number.startswith("+") and not number.startswith("0"):
        number = "+265" + number.lstrip("265")
    current_user.whatsapp_number = number
    current_user.whatsapp_optin = True
    await db.commit()
    return {"status": "ok", "whatsapp_number": number, "whatsapp_optin": True}


@router.post("/optout")
async def whatsapp_optout(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    current_user.whatsapp_optin = False
    await db.commit()
    return {"status": "ok", "whatsapp_optin": False}


@router.get("/status")
async def notification_status(
    current_user: User = Depends(get_current_user),
):
    return {
        "whatsapp_number": current_user.whatsapp_number,
        "whatsapp_optin": current_user.whatsapp_optin or False,
    }


@router.post("/send")
async def send_notification(
    data: SendNotificationRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    log = await NotificationService.notify(
        db=db,
        phone=data.phone,
        message=data.message,
        channel=data.channel,
        user_id=data.user_id or current_user.id,
        patient_id=data.patient_id,
        template=data.template,
    )
    if log.status == NotificationStatus.FAILED:
        raise HTTPException(status_code=502, detail="Notification delivery failed")
    return {"status": "sent", "id": log.id}


@router.get("/history")
async def notification_history(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NotificationLog)
        .where(NotificationLog.user_id == current_user.id)
        .order_by(NotificationLog.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()
