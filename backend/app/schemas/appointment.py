from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models import AppointmentStatus, AppointmentPriority


class AppointmentCreate(BaseModel):
    patient_id: int
    appointment_date: datetime
    appointment_type: str
    department: Optional[str] = None
    clinician_id: Optional[int] = None
    clinician_name: Optional[str] = None
    location: Optional[str] = None
    end_time: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    priority: AppointmentPriority = AppointmentPriority.ROUTINE
    is_teleconsult: bool = False


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    appointment_date: datetime
    appointment_type: str
    department: Optional[str] = None
    clinician_name: Optional[str] = None
    location: Optional[str] = None
    end_time: Optional[datetime] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: AppointmentStatus
    priority: AppointmentPriority
    is_teleconsult: bool
    checked_in_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QueueResponse(BaseModel):
    id: int
    visit_id: int
    patient_id: int
    department: str
    queue_type: str
    position: Optional[int] = None
    status: str
    room: Optional[str] = None

    class Config:
        from_attributes = True
