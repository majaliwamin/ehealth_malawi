from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum as SAEnum, Boolean
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class VisitType(enum.Enum):
    OPD = "outpatient"
    IPD = "inpatient"
    EMERGENCY = "emergency"
    REFERRAL = "referral"
    REVIEW = "review"
    TELEMEDICINE = "telemedicine"


class TriageCategory(enum.Enum):
    IMMEDIATE = "immediate"
    EMERGENCY = "emergency"
    URGENT = "urgent"
    SEMI_URGENT = "semi_urgent"
    NON_URGENT = "non_urgent"
    EXPECTANT = "expectant"


class VisitStatus(enum.Enum):
    WAITING = "waiting"
    IN_CONSULTATION = "in_consultation"
    ADMITTED = "admitted"
    DISCHARGED = "discharged"
    TRANSFERRED = "transferred"
    CANCELLED = "cancelled"
    DID_NOT_ATTEND = "did_not_attend"


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    visit_type = Column(SAEnum(VisitType), nullable=False)
    visit_date = Column(DateTime(timezone=True), server_default=func.now())
    presenting_complaint = Column(Text, nullable=True)
    history_of_presenting_illness = Column(Text, nullable=True)

    triage_category = Column(SAEnum(TriageCategory), nullable=True)
    triage_notes = Column(Text, nullable=True)
    triaged_by = Column(Integer, nullable=True)
    triage_time = Column(DateTime(timezone=True), nullable=True)

    status = Column(SAEnum(VisitStatus), default=VisitStatus.WAITING)
    queue_position = Column(Integer, nullable=True)
    consultation_room = Column(String(50), nullable=True)

    department = Column(String(100), nullable=True)
    ward = Column(String(100), nullable=True)
    bed_number = Column(String(50), nullable=True)

    referred_from = Column(String(200), nullable=True)
    referred_to = Column(String(200), nullable=True)
    referral_notes = Column(Text, nullable=True)

    admitted_at = Column(DateTime(timezone=True), nullable=True)
    discharged_at = Column(DateTime(timezone=True), nullable=True)
    discharge_disposition = Column(String(100), nullable=True)
    discharge_summary = Column(Text, nullable=True)

    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class VitalSign(Base):
    __tablename__ = "vital_signs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    visit_id = Column(Integer, nullable=True)

    systolic_bp = Column(Integer, nullable=True)
    diastolic_bp = Column(Integer, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    respiratory_rate = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)
    oxygen_saturation = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    blood_glucose = Column(Float, nullable=True)
    pain_score = Column(Integer, nullable=True)
    gcs_score = Column(Integer, nullable=True)
    gcs_eye = Column(Integer, nullable=True)
    gcs_verbal = Column(Integer, nullable=True)
    gcs_motor = Column(Integer, nullable=True)
    muac_cm = Column(Float, nullable=True)
    head_circumference_cm = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)
    recorded_by = Column(Integer, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class ClinicalNote(Base):
    __tablename__ = "clinical_notes"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    visit_id = Column(Integer, nullable=True)

    note_type = Column(String(50), nullable=False, comment="SOAP, progress, consultation, nursing, discharge")
    subjective = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    plan = Column(Text, nullable=True)

    diagnosis_codes = Column(Text, nullable=True)
    procedure_codes = Column(Text, nullable=True)

    is_unsigned = Column(Boolean, default=True)
    signed_by = Column(Integer, nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    cosigned_by = Column(Integer, nullable=True)
    cosigned_at = Column(DateTime(timezone=True), nullable=True)

    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class NursingNote(Base):
    __tablename__ = "nursing_notes"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    visit_id = Column(Integer, nullable=True)

    note_type = Column(String(50), nullable=False, comment="shift_report, observation, care_given, incident")
    observation = Column(Text, nullable=True)
    care_given = Column(Text, nullable=True)
    patient_response = Column(Text, nullable=True)
    fluid_intake_ml = Column(Float, nullable=True)
    fluid_output_ml = Column(Float, nullable=True)
    nutrition_intake = Column(String(200), nullable=True)
    bowel_movement = Column(String(100), nullable=True)
    skin_integrity = Column(String(100), nullable=True)
    fall_risk_score = Column(Integer, nullable=True)
    pain_assessment = Column(String(100), nullable=True)

    shift = Column(String(50), nullable=True)
    reported_to = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
