from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SAEnum, Boolean
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DID_NOT_ATTEND = "did_not_attend"
    RESCHEDULED = "rescheduled"


class AppointmentPriority(enum.Enum):
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)

    appointment_type = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    clinician_id = Column(Integer, nullable=True)
    clinician_name = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    status = Column(SAEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    priority = Column(SAEnum(AppointmentPriority), default=AppointmentPriority.ROUTINE)

    is_teleconsult = Column(Boolean, default=False)
    teleconsult_link = Column(String(500), nullable=True)

    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    checked_in_by = Column(Integer, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    rescheduled_from = Column(Integer, nullable=True)

    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime(timezone=True), nullable=True)

    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Queue(Base):
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, nullable=False, index=True)
    patient_id = Column(Integer, nullable=False, index=True)

    department = Column(String(100), nullable=False)
    queue_type = Column(String(50), nullable=False, comment="triage, consultation, pharmacy, lab, procedure")
    priority = Column(Integer, default=0)
    position = Column(Integer, nullable=True)

    status = Column(String(50), default="waiting")
    called_at = Column(DateTime(timezone=True), nullable=True)
    called_count = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    target_clinician = Column(Integer, nullable=True)
    room = Column(String(50), nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
