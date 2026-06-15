from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from ..models import Gender


class PatientCreate(BaseModel):
    national_id: Optional[str] = None
    file_number: Optional[str] = None
    surname: str
    first_name: str
    middle_name: Optional[str] = None
    date_of_birth: date
    gender: Gender
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    home_district: Optional[str] = None
    traditional_authority: Optional[str] = None
    village: Optional[str] = None
    current_residence: Optional[str] = None
    landmark: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    occupation: Optional[str] = None
    marital_status: Optional[str] = None


class PatientUpdate(BaseModel):
    surname: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    home_district: Optional[str] = None
    traditional_authority: Optional[str] = None
    village: Optional[str] = None
    current_residence: Optional[str] = None
    landmark: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    occupation: Optional[str] = None
    marital_status: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    passport_id: Optional[str] = None
    national_id: Optional[str] = None
    file_number: Optional[str] = None
    surname: str
    first_name: str
    middle_name: Optional[str] = None
    date_of_birth: date
    gender: Gender
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    home_district: Optional[str] = None
    traditional_authority: Optional[str] = None
    village: Optional[str] = None
    current_residence: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatientSearchResult(BaseModel):
    id: int
    passport_id: Optional[str] = None
    surname: str
    first_name: str
    date_of_birth: date
    gender: Gender
    phone: Optional[str] = None
    home_district: Optional[str] = None
    village: Optional[str] = None
