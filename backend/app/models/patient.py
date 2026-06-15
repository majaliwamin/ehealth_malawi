from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Text, Enum as SAEnum, ForeignKey
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodGroup(enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    passport_id = Column(String(50), unique=True, index=True, comment="Unique eHealth Passport ID")
    national_id = Column(String(50), unique=True, nullable=True)
    file_number = Column(String(50), unique=True, nullable=True)

    surname = Column(String(100), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(SAEnum(Gender), nullable=False)
    blood_group = Column(String(10), nullable=True)

    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    home_district = Column(String(100), nullable=True)
    traditional_authority = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)
    current_residence = Column(String(200), nullable=True)
    landmark = Column(String(200), nullable=True)

    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_relation = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)
    emergency_contact_district = Column(String(100), nullable=True)

    next_of_kin_name = Column(String(200), nullable=True)
    next_of_kin_phone = Column(String(50), nullable=True)

    occupation = Column(String(100), nullable=True)
    marital_status = Column(String(50), nullable=True)

    is_active = Column(Boolean, default=True)
    is_deceased = Column(Boolean, default=False)
    death_date = Column(DateTime, nullable=True)
    death_cause = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)

class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    allergen = Column(String(200), nullable=False)
    reaction = Column(Text, nullable=True)
    severity = Column(String(50), default="moderate")
    onset_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    icd_code = Column(String(20), nullable=True)
    diagnosis_name = Column(String(300), nullable=False)
    diagnosis_type = Column(String(50), default="provisional")
    certainty = Column(String(50), default="suspected")
    onset_date = Column(Date, nullable=True)
    resolution_date = Column(Date, nullable=True)
    is_chronic = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    clinician_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
