from pydantic import BaseModel
from typing import Optional
from ..models import UserRole


class LoginRequest(BaseModel):
    username: str
    password: str
    role: Optional[UserRole] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: UserRole
    full_name: str
    whatsapp_number: Optional[str] = None
    whatsapp_optin: bool = False


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    surname: str
    first_name: str
    role: UserRole
    designation: Optional[str] = None
    license_number: Optional[str] = None
    department: Optional[str] = None
    facility: Optional[str] = None
    district: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    surname: str
    first_name: str
    role: UserRole
    designation: Optional[str] = None
    department: Optional[str] = None
    facility: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
