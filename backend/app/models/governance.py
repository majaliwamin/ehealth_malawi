from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Date, Enum as SAEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class IncidentSeverity(enum.Enum):
    NEAR_MISS = "near_miss"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    FATAL = "fatal"
    SENTINEL = "sentinel"


class IncidentCategory(enum.Enum):
    MEDICATION_ERROR = "medication_error"
    FALL = "fall"
    HAI = "healthcare_associated_infection"
    SURGICAL_COMPLICATION = "surgical_complication"
    DIAGNOSTIC_ERROR = "diagnostic_error"
    EQUIPMENT_FAILURE = "equipment_failure"
    PATIENT_IDENTITY = "patient_identity"
    COMMUNICATION = "communication"
    BLOOD_TRANSFUSION = "blood_transfusion"
    MATERNAL = "maternal"
    NEONATAL = "neonatal"
    OTHER = "other"


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=True)
    incident_number = Column(String(50), unique=True, nullable=True)

    category = Column(SAEnum(IncidentCategory), nullable=False)
    severity = Column(SAEnum(IncidentSeverity), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(200), nullable=True)
    datetime_occurred = Column(DateTime(timezone=True), nullable=False)
    datetime_reported = Column(DateTime(timezone=True), server_default=func.now())

    reported_by = Column(Integer, nullable=False)
    reported_by_role = Column(String(100), nullable=True)
    involved_staff = Column(Text, nullable=True)

    immediate_action = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    contributing_factors = Column(Text, nullable=True)
    corrective_actions = Column(Text, nullable=True)
    prevention_plan = Column(Text, nullable=True)

    investigation_status = Column(String(50), default="open")
    investigated_by = Column(Integer, nullable=True)
    investigation_notes = Column(Text, nullable=True)

    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    closed_by = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    patient_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)
    user_role = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(300), nullable=True)
    details = Column(Text, nullable=True)
    changes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class QualityIndicator(Base):
    __tablename__ = "quality_indicators"

    id = Column(Integer, primary_key=True, index=True)
    indicator_name = Column(String(300), nullable=False)
    indicator_type = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    numerator = Column(Integer, nullable=True)
    denominator = Column(Integer, nullable=True)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MortalityReview(Base):
    __tablename__ = "mortality_reviews"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    visit_id = Column(Integer, nullable=True)
    date_of_death = Column(DateTime(timezone=True), nullable=False)
    primary_cause = Column(String(300), nullable=False)
    contributing_causes = Column(Text, nullable=True)
    maternal_death = Column(Boolean, default=False)
    neonatal_death = Column(Boolean, default=False)
    perinatal_death = Column(Boolean, default=False)
    surgical_death = Column(Boolean, default=False)
    preventable = Column(Boolean, nullable=True)
    reviewed_by = Column(Integer, nullable=True)
    review_notes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
