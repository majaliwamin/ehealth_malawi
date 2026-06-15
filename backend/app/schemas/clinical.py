from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models import VisitType, TriageCategory, VisitStatus


class VisitCreate(BaseModel):
    patient_id: int
    visit_type: VisitType
    presenting_complaint: Optional[str] = None
    history_of_presenting_illness: Optional[str] = None
    department: Optional[str] = None
    referred_from: Optional[str] = None
    referral_notes: Optional[str] = None


class VisitResponse(BaseModel):
    id: int
    patient_id: int
    visit_type: VisitType
    visit_date: Optional[datetime] = None
    presenting_complaint: Optional[str] = None
    triage_category: Optional[TriageCategory] = None
    status: VisitStatus
    department: Optional[str] = None
    ward: Optional[str] = None
    bed_number: Optional[str] = None
    referred_from: Optional[str] = None
    referred_to: Optional[str] = None
    admitted_at: Optional[datetime] = None
    discharged_at: Optional[datetime] = None
    discharge_disposition: Optional[str] = None

    class Config:
        from_attributes = True


class VitalSignCreate(BaseModel):
    patient_id: int
    visit_id: Optional[int] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    temperature: Optional[float] = None
    oxygen_saturation: Optional[float] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    blood_glucose: Optional[float] = None
    pain_score: Optional[int] = None
    gcs_score: Optional[int] = None
    muac_cm: Optional[float] = None


class VitalSignResponse(BaseModel):
    id: int
    patient_id: int
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    temperature: Optional[float] = None
    oxygen_saturation: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    recorded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClinicalNoteCreate(BaseModel):
    patient_id: int
    visit_id: Optional[int] = None
    note_type: str
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    diagnosis_codes: Optional[str] = None


class ClinicalNoteResponse(BaseModel):
    id: int
    patient_id: int
    note_type: str
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    is_unsigned: bool
    signed_by: Optional[int] = None
    created_by: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
