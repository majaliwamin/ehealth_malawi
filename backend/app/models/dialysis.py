from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Date, Enum as SAEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class DialysisType(enum.Enum):
    HEMODIALYSIS = "hemodialysis"
    PERITONEAL_DIALYSIS = "peritoneal_dialysis"
    CRRT = "continuous_renal_replacement_therapy"
    SLED = "sustained_low_efficiency_dialysis"


class DialysisAccess(enum.Enum):
    AV_FISTULA = "av_fistula"
    AV_GRAFT = "av_graft"
    TUNNELED_CATHETER = "tunneled_catheter"
    NON_TUNNELED_CATHETER = "non_tunneled_catheter"
    PERITONEAL_CATHETER = "peritoneal_catheter"


class DialysisSession(Base):
    __tablename__ = "dialysis_sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    visit_id = Column(Integer, nullable=True)
    session_number = Column(Integer, nullable=True)

    dialysis_type = Column(SAEnum(DialysisType), nullable=False)
    access_type = Column(SAEnum(DialysisAccess), nullable=True)

    pre_weight_kg = Column(Float, nullable=True)
    post_weight_kg = Column(Float, nullable=True)
    ultrafiltration_ml = Column(Float, nullable=True)
    target_uf_ml = Column(Float, nullable=True)

    pre_bp_systolic = Column(Integer, nullable=True)
    pre_bp_diastolic = Column(Integer, nullable=True)
    post_bp_systolic = Column(Integer, nullable=True)
    post_bp_diastolic = Column(Integer, nullable=True)
    pre_hr = Column(Integer, nullable=True)
    post_hr = Column(Integer, nullable=True)

    dialyzer_type = Column(String(100), nullable=True)
    dialysate_flow = Column(Integer, nullable=True)
    blood_flow = Column(Integer, nullable=True)
    heparin_dose = Column(String(100), nullable=True)
    potassium_bath = Column(String(50), nullable=True)
    calcium_bath = Column(String(50), nullable=True)
    bicarbonate = Column(String(50), nullable=True)
    temperature = Column(Float, nullable=True)

    duration_minutes = Column(Integer, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)

    complications = Column(Text, nullable=True)
    access_assessment = Column(Text, nullable=True)
    nurse_notes = Column(Text, nullable=True)
    machine_number = Column(String(50), nullable=True)

    performed_by = Column(Integer, nullable=True)
    verified_by = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CKDStage(enum.Enum):
    STAGE_1 = "stage_1"
    STAGE_2 = "stage_2"
    STAGE_3A = "stage_3a"
    STAGE_3B = "stage_3b"
    STAGE_4 = "stage_4"
    STAGE_5 = "stage_5"
    ESRD = "end_stage_renal_disease"


class ChronicKidneyDiseaseRecord(Base):
    __tablename__ = "ckd_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)

    ckd_stage = Column(SAEnum(CKDStage), nullable=True)
    egfr = Column(Float, nullable=True)
    serum_creatinine = Column(Float, nullable=True)
    bun = Column(Float, nullable=True)
    albumin = Column(Float, nullable=True)
    hemoglobin = Column(Float, nullable=True)
    calcium = Column(Float, nullable=True)
    phosphate = Column(Float, nullable=True)
    pth = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    bicarbonate = Column(Float, nullable=True)

    proteinuria_dipstick = Column(String(50), nullable=True)
    upcr = Column(Float, nullable=True)

    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)

    anemia_status = Column(String(100), nullable=True)
    bone_mineral_status = Column(String(100), nullable=True)
    nutrition_status = Column(String(100), nullable=True)

    medications = Column(Text, nullable=True)
    diet_plan = Column(Text, nullable=True)
    nephrologist_id = Column(Integer, nullable=True)

    next_follow_up = Column(Date, nullable=True)
    next_dialysis_appointment = Column(DateTime(timezone=True), nullable=True)

    notes = Column(Text, nullable=True)
    recorded_by = Column(Integer, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
