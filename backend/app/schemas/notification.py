from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models import NotificationChannel, NotificationStatus


class SendNotificationRequest(BaseModel):
    user_id: Optional[int] = None
    patient_id: Optional[int] = None
    phone: str
    message: str
    channel: NotificationChannel = NotificationChannel.WHATSAPP
    template: Optional[str] = None


class NotificationLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    patient_id: Optional[int]
    recipient: str
    channel: NotificationChannel
    message: str
    status: NotificationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class WhatsAppOptinRequest(BaseModel):
    whatsapp_number: str
