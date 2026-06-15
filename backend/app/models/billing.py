from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, Enum as SAEnum, ForeignKey
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class PaymentMethod(enum.Enum):
    MPAMBA = "mpamba"
    AIRTEL_MONEY = "airtel_money"
    BANK = "bank"


class PaymentStatus(enum.Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    CANCELLED = "cancelled"


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="unpaid", nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    patient_name = Column(String(200), nullable=False)
    patient_phone = Column(String(50), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    payment_method = Column(String(20), nullable=True)
    account_number = Column(String(100), nullable=True)
    receipt_ref = Column(String(50), unique=True, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
