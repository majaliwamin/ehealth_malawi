from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum as SAEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class ICUScoreType(enum.Enum):
    SOFA = "sofa"
    APACHE_II = "apache_ii"
    SAPS_II = "saps_ii"
    MPM_II = "mpm_ii"
    NEWS2 = "news2"
    qSOFA = "qsofa"
    FOUR = "four"
    RASS = "rass"
    CAM_ICU = "cam_icu"


class VentilationMode(enum.Enum):
    AC = "assist_control"
    SIMV = "synchronized_intermittent_mandatory"
    PSV = "pressure_support"
    PCV = "pressure_control"
    VCV = "volume_control"
    CPAP = "cpap"
    BIPAP = "bipap"
    HFNC = "high_flow_nasal_cannula"
    NIV = "non_invasive"
    HFOV = "high_frequency_oscillatory"


class ICUAdmission(Base):
    __tablename__ = "icu_admissions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    visit_id = Column(Integer, nullable=True)

    admission_date = Column(DateTime(timezone=True), nullable=False)
    discharge_date = Column(DateTime(timezone=True), nullable=True)
    icu_type = Column(String(100), nullable=True, comment="ICU, HDU, CCU, NICU, PICU")
    bed_number = Column(String(50), nullable=True)

    admission_source = Column(String(100), nullable=True)
    admitting_diagnosis = Column(Text, nullable=True)
    admitting_service = Column(String(100), nullable=True)

    is_ventilated = Column(Boolean, default=False)
    ventilation_mode = Column(SAEnum(VentilationMode), nullable=True)
    fio2 = Column(Float, nullable=True)
    peep = Column(Float, nullable=True)
    tidal_volume = Column(Float, nullable=True)
    respiratory_rate_set = Column(Integer, nullable=True)

    on_vasopressors = Column(Boolean, default=False)
    vasopressor_drugs = Column(Text, nullable=True)
    on_renal_replacement = Column(Boolean, default=False)
    rrt_type = Column(String(100), nullable=True)

    gcs_on_admission = Column(Integer, nullable=True)
    sofa_score = Column(Integer, nullable=True)
    apache_score = Column(Integer, nullable=True)

    discharge_status = Column(String(50), nullable=True)
    discharge_destination = Column(String(100), nullable=True)
    discharge_notes = Column(Text, nullable=True)

    attending_physician = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ICUScore(Base):
    __tablename__ = "icu_scores"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    icu_admission_id = Column(Integer, nullable=True)

    score_type = Column(SAEnum(ICUScoreType), nullable=False)
    score_value = Column(Float, nullable=False)
    score_interpretation = Column(String(200), nullable=True)

    recorded_at = Column(DateTime(timezone=True), nullable=False)
    recorded_by = Column(Integer, nullable=True)

    qsofa_rr = Column(Integer, nullable=True)
    qsofa_sbp = Column(Integer, nullable=True)
    qsofa_gcs = Column(Integer, nullable=True)

    sofa_respiration = Column(Integer, nullable=True)
    sofa_coagulation = Column(Integer, nullable=True)
    sofa_liver = Column(Integer, nullable=True)
    sofa_cardiovascular = Column(Integer, nullable=True)
    sofa_cns = Column(Integer, nullable=True)
    sofa_renal = Column(Integer, nullable=True)

    rass_score = Column(Integer, nullable=True)
    cam_icu_positive = Column(Boolean, nullable=True)
    four_score = Column(Integer, nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FluidBalance(Base):
    __tablename__ = "fluid_balance"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    visit_id = Column(Integer, nullable=True)
    icu_admission_id = Column(Integer, nullable=True)

    intake_type = Column(String(100), nullable=False)
    intake_amount_ml = Column(Float, nullable=False)
    output_type = Column(String(100), nullable=True)
    output_amount_ml = Column(Float, nullable=True)
    net_balance_ml = Column(Float, nullable=True)

    recorded_at = Column(DateTime(timezone=True), nullable=False)
    recorded_by = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
