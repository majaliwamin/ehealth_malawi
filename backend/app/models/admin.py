from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum as SAEnum, Boolean
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    HOSPITAL_ADMIN = "hospital_admin"
    DEPARTMENT_IN_CHARGE = "department_in_charge"
    DISTRICT_HEALTH_OFFICER = "district_health_officer"
    OMBUDSMAN = "ombudsman"
    DOCTOR = "doctor"
    NURSE = "nurse"
    CLINICAL_OFFICER = "clinical_officer"
    MEDICAL_ASSISTANT = "medical_assistant"
    PHARMACIST = "pharmacist"
    LAB_TECHNICIAN = "lab_technician"
    RADIOGRAPHER = "radiographer"
    MIDWIFE = "midwife"
    HEALTH_SURVEILLANCE_ASSISTANT = "health_surveillance_assistant"
    DATA_ENTRY = "data_entry"
    STUDENT = "student"
    RESEARCHER = "researcher"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(50), unique=True, nullable=True)
    hashed_password = Column(String(200), nullable=False)

    surname = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    role = Column(SAEnum(UserRole), nullable=False)
    designation = Column(String(200), nullable=True)
    license_number = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    facility = Column(String(200), nullable=True)
    district = Column(String(100), nullable=True)
    supervisor_id = Column(Integer, nullable=True)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    requires_password_change = Column(Boolean, default=True)
    two_factor_enabled = Column(Boolean, default=False)
    whatsapp_number = Column(String(50), nullable=True)
    whatsapp_optin = Column(Boolean, default=False)

    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=True)
    description = Column(Text, nullable=True)
    facility = Column(String(200), nullable=True)
    head_of_department = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    code = Column(String(50), unique=True, nullable=True)
    type = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    level = Column(String(50), nullable=True, comment="health_centre, district_hospital, central_hospital, referral")
    bed_capacity = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditTrail(Base):
    __tablename__ = "audit_trails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(200), nullable=False)
    resource = Column(String(200), nullable=False)
    resource_id = Column(Integer, nullable=True)
    patient_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(300), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
