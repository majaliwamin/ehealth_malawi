from pydantic import BaseModel
from typing import Optional


class PatientRegister(BaseModel):
    full_name: str
    date_of_birth: str
    gender: str
    phone: str
    email: Optional[str] = None
    district: Optional[str] = None
    traditional_authority: Optional[str] = None
    village: Optional[str] = None
    occupation: Optional[str] = None


class PatientLogin(BaseModel):
    passport_id: str
    phone: str


class PatientToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    district: Optional[str] = None
    traditional_authority: Optional[str] = None
    village: Optional[str] = None
    occupation: Optional[str] = None
