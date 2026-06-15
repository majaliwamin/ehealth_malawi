from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum as SAEnum
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class AnnouncementCategory(enum.Enum):
    CRITICAL = "critical"
    PUBLIC_HEALTH = "public_health"
    SERVICE = "service"
    ADMIN = "admin"


class AnnouncementPriority(enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=True)
    category = Column(String(20), default="public_health", nullable=False)
    priority = Column(String(10), default="medium", nullable=False)
    facility_id = Column(Integer, nullable=True)
    target_role = Column(String(30), nullable=True)
    created_by = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    expiry_date = Column(DateTime, nullable=True)
    read_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
