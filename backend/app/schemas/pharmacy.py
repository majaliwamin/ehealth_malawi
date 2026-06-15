from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models import PrescriptionStatus, MedicationRoute


class PrescriptionItemCreate(BaseModel):
    medication_name: str
    medication_code: Optional[str] = None
    generic_name: Optional[str] = None
    strength: Optional[str] = None
    dosage: str
    route: MedicationRoute
    frequency: str
    duration_days: Optional[int] = None
    duration_text: Optional[str] = None
    quantity: Optional[int] = None
    instructions: Optional[str] = None
    indication: Optional[str] = None


class PrescriptionCreate(BaseModel):
    patient_id: int
    visit_id: Optional[int] = None
    prescribed_by_name: Optional[str] = None
    diagnosis_code: Optional[str] = None
    clinical_indication: Optional[str] = None
    notes: Optional[str] = None
    is_emergency: bool = False
    items: List[PrescriptionItemCreate]


class DispenseRequest(BaseModel):
    dispensed_by: Optional[int] = None
    dispense_notes: Optional[str] = None
    status: PrescriptionStatus = PrescriptionStatus.DISPENSED


class PrescriptionResponse(BaseModel):
    id: int
    patient_id: int
    prescription_number: Optional[str] = None
    prescribed_by_name: Optional[str] = None
    status: PrescriptionStatus
    is_emergency: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
