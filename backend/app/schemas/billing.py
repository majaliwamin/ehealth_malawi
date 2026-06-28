from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.billing import PaymentMethod, PaymentStatus


class BillCreate(BaseModel):
    title: str
    description: Optional[str] = None
    amount: float
    patient_id: int
    patient_name: str
    patient_phone: Optional[str] = None


class BillUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[PaymentStatus] = None


class PaymentRequest(BaseModel):
    payment_method: PaymentMethod
    account_number: str
    pin_hash: str = ""


class BillResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    amount: float
    status: PaymentStatus
    patient_id: int
    patient_name: str
    patient_phone: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    account_number: Optional[str] = None
    receipt_ref: Optional[str] = None
    paid_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReceiptResponse(BaseModel):
    receipt_ref: str
    title: str
    amount: float
    patient_name: str
    payment_method: PaymentMethod
    account_number: str
    paid_date: datetime
    share_text: str
