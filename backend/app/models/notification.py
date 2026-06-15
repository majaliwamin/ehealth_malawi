from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum as SAEnum
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class NotificationChannel(enum.Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"


class NotificationStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    patient_id = Column(Integer, nullable=True)
    recipient = Column(String(50), nullable=False)
    channel = Column(SAEnum(NotificationChannel), nullable=False)
    template = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(SAEnum(NotificationStatus), default=NotificationStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
