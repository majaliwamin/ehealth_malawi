import httpx
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.config import settings
from ..models import NotificationLog, NotificationChannel, NotificationStatus, User

logger = logging.getLogger(__name__)


class NotificationService:

    @staticmethod
    async def send_whatsapp(phone: str, message: str) -> bool:
        if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_ID:
            logger.warning("WhatsApp API not configured — falling back to SMS")
            return await NotificationService.send_sms(phone, message)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_ID}/messages",
                    json={
                        "messaging_product": "whatsapp",
                        "to": phone.lstrip("+"),
                        "type": "text",
                        "text": {"body": message},
                    },
                    headers={
                        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
                        "Content-Type": "application/json",
                    },
                )
                if resp.status_code == 200:
                    return True
                logger.error("WhatsApp send failed: %s - %s", resp.status_code, resp.text)
                return False
        except Exception as e:
            logger.error("WhatsApp send error: %s", e)
            return False

    @staticmethod
    async def send_sms(phone: str, message: str) -> bool:
        if not settings.AT_API_KEY or not settings.AT_USERNAME:
            logger.warning("SMS API not configured — notification not sent")
            return False
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://api.africastalking.com/version1/messaging",
                    data={
                        "username": settings.AT_USERNAME,
                        "to": phone,
                        "message": message,
                    },
                    headers={
                        "ApiKey": settings.AT_API_KEY,
                        "Accept": "application/json",
                    },
                )
                if resp.status_code == 201:
                    return True
                logger.error("SMS send failed: %s - %s", resp.status_code, resp.text)
                return False
        except Exception as e:
            logger.error("SMS send error: %s", e)
            return False

    @classmethod
    async def notify(
        cls,
        db: AsyncSession,
        phone: str,
        message: str,
        channel: NotificationChannel = NotificationChannel.WHATSAPP,
        user_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        template: Optional[str] = None,
    ) -> NotificationLog:
        if channel == NotificationChannel.WHATSAPP:
            success = await cls.send_whatsapp(phone, message)
        else:
            success = await cls.send_sms(phone, message)

        log = NotificationLog(
            user_id=user_id,
            patient_id=patient_id,
            recipient=phone,
            channel=channel,
            message=message,
            template=template,
            status=NotificationStatus.SENT if success else NotificationStatus.FAILED,
            error_message=None if success else "Provider returned failure",
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def get_user_phone(user_id: int, db: AsyncSession) -> Optional[str]:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user and user.whatsapp_optin and user.whatsapp_number:
            return user.whatsapp_number
        if user and user.phone:
            return user.phone
        return None
