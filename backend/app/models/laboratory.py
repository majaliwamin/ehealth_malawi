from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum as SAEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class LabOrderStatus(enum.Enum):
    ORDERED = "ordered"
    SPECIMEN_COLLECTED = "specimen_collected"
    SPECIMEN_RECEIVED = "specimen_received"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CANCELLED = "cancelled"


class SpecimenType(enum.Enum):
    BLOOD = "blood"
    URINE = "urine"
    STOOL = "stool"
    SPUTUM = "sputum"
    CSF = "csf"
    TISSUE = "tissue"
    SWAB = "swab"
    OTHER = "other"


class LabOrder(Base):
    __tablename__ = "lab_orders"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    visit_id = Column(Integer, nullable=True)
    order_number = Column(String(50), unique=True, nullable=True)

    clinician_id = Column(Integer, nullable=True)
    clinician_name = Column(String(200), nullable=True)
    clinical_indication = Column(Text, nullable=True)
    diagnosis_code = Column(String(20), nullable=True)
    is_urgent = Column(Boolean, default=False)

    specimen_type = Column(SAEnum(SpecimenType), nullable=True)
    specimen_id = Column(String(100), nullable=True)
    specimen_collected_at = Column(DateTime(timezone=True), nullable=True)
    specimen_collected_by = Column(Integer, nullable=True)
    specimen_received_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(SAEnum(LabOrderStatus), default=LabOrderStatus.ORDERED)
    lab_technician_id = Column(Integer, nullable=True)
    verified_by = Column(Integer, nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    result_notes = Column(Text, nullable=True)
    cancelled_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tests = relationship("LabTest", back_populates="order", cascade="all, delete-orphan")


class LabTest(Base):
    __tablename__ = "lab_tests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("lab_orders.id"), nullable=False)
    test_name = Column(String(200), nullable=False)
    test_code = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)

    result_value = Column(String(200), nullable=True)
    result_unit = Column(String(50), nullable=True)
    reference_range_low = Column(String(50), nullable=True)
    reference_range_high = Column(String(50), nullable=True)
    is_abnormal = Column(Boolean, default=False)
    result_text = Column(Text, nullable=True)
    result_qualitative = Column(String(100), nullable=True)

    performed_by = Column(Integer, nullable=True)
    performed_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("LabOrder", back_populates="tests")


class RadiologyOrder(Base):
    __tablename__ = "radiology_orders"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    visit_id = Column(Integer, nullable=True)
    order_number = Column(String(50), unique=True, nullable=True)

    study_type = Column(String(200), nullable=False)
    body_part = Column(String(200), nullable=True)
    clinical_indication = Column(Text, nullable=True)
    is_urgent = Column(Boolean, default=False)

    status = Column(String(50), default="ordered")
    ordered_by = Column(Integer, nullable=True)
    ordered_at = Column(DateTime(timezone=True), server_default=func.now())
    performed_at = Column(DateTime(timezone=True), nullable=True)
    reported_at = Column(DateTime(timezone=True), nullable=True)

    findings = Column(Text, nullable=True)
    impression = Column(Text, nullable=True)
    report = Column(Text, nullable=True)
    reported_by = Column(Integer, nullable=True)

    image_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
