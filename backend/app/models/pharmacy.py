from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Date, Enum as SAEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class PrescriptionStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISPENSED = "dispensed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class MedicationRoute(enum.Enum):
    ORAL = "oral"
    INTRAVENOUS = "intravenous"
    INTRAMUSCULAR = "intramuscular"
    SUBCUTANEOUS = "subcutaneous"
    TOPICAL = "topical"
    INHALATION = "inhalation"
    RECTAL = "rectal"
    SUBLINGUAL = "sublingual"
    INTRATHECAL = "intrathecal"
    OTHER = "other"


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    visit_id = Column(Integer, nullable=True)
    prescription_number = Column(String(50), unique=True, nullable=True)

    prescribed_by = Column(Integer, nullable=True)
    prescribed_by_name = Column(String(200), nullable=True)
    prescribed_at = Column(DateTime(timezone=True), server_default=func.now())
    diagnosis_code = Column(String(20), nullable=True)

    status = Column(SAEnum(PrescriptionStatus), default=PrescriptionStatus.ACTIVE)
    is_emergency = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    clinical_indication = Column(Text, nullable=True)

    dispensed_by = Column(Integer, nullable=True)
    dispensed_at = Column(DateTime(timezone=True), nullable=True)
    dispense_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)

    medication_name = Column(String(300), nullable=False)
    medication_code = Column(String(50), nullable=True)
    generic_name = Column(String(200), nullable=True)
    strength = Column(String(100), nullable=True)
    formulation = Column(String(100), nullable=True)

    dosage = Column(String(100), nullable=False)
    route = Column(SAEnum(MedicationRoute), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=True)
    duration_text = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=True)
    quantity_unit = Column(String(50), nullable=True)

    instructions = Column(Text, nullable=True)
    indication = Column(String(300), nullable=True)
    is_controlled = Column(Boolean, default=False)

    dispensed_quantity = Column(Integer, nullable=True)
    dispensed_by = Column(Integer, nullable=True)
    dispensed_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(String(50), default="active")
    discontinue_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    prescription = relationship("Prescription", back_populates="items")


class MedicationAdministration(Base):
    __tablename__ = "medication_administrations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    prescription_item_id = Column(Integer, nullable=True)
    visit_id = Column(Integer, nullable=True)

    medication_name = Column(String(300), nullable=False)
    dose_administered = Column(String(100), nullable=False)
    route = Column(String(50), nullable=False)
    site = Column(String(100), nullable=True)

    administered_at = Column(DateTime(timezone=True), nullable=False)
    administered_by = Column(Integer, nullable=False)
    witnessed_by = Column(Integer, nullable=True)

    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(Date, nullable=True)

    reaction_notes = Column(Text, nullable=True)
    omitted = Column(Boolean, default=False)
    omission_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DrugStock(Base):
    __tablename__ = "drug_stock"

    id = Column(Integer, primary_key=True, index=True)
    medication_code = Column(String(50), nullable=True, index=True)
    medication_name = Column(String(300), nullable=False)
    generic_name = Column(String(200), nullable=True)
    strength = Column(String(100), nullable=True)
    formulation = Column(String(100), nullable=True)

    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(Date, nullable=True)
    quantity_in_stock = Column(Integer, default=0)
    unit_of_measure = Column(String(50), nullable=True)
    reorder_level = Column(Integer, default=10)
    unit_cost = Column(Float, nullable=True)
    supplier = Column(String(200), nullable=True)

    location = Column(String(100), nullable=True)
    is_controlled = Column(Boolean, default=False)
    requires_prescription = Column(Boolean, default=True)

    last_restocked_at = Column(DateTime(timezone=True), nullable=True)
    last_restocked_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
