from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime
from ....core.database import get_async_session
from ....middleware.auth import get_current_user
from ....models import Bill, User
from ....models.billing import PaymentStatus
from ....schemas.billing import BillCreate, BillUpdate, PaymentRequest, BillResponse, ReceiptResponse

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/bills", response_model=BillResponse, status_code=201)
async def create_bill(data: BillCreate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    bill = Bill(
        title=data.title,
        description=data.description,
        amount=data.amount,
        patient_id=data.patient_id,
        patient_name=data.patient_name,
        patient_phone=data.patient_phone,
        created_by=current_user.id,
    )
    db.add(bill)
    await db.commit()
    await db.refresh(bill)
    return bill


@router.get("/bills", response_model=List[BillResponse])
async def list_bills(db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Bill).order_by(desc(Bill.created_at)))
    return result.scalars().all()


@router.get("/bills/{bill_id}", response_model=BillResponse)
async def get_bill(bill_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Bill).where(Bill.id == bill_id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.get("/patient/{patient_id}", response_model=List[BillResponse])
async def get_patient_bills(patient_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Bill).where(Bill.patient_id == patient_id).order_by(desc(Bill.created_at))
    )
    return result.scalars().all()


@router.post("/bills/{bill_id}/pay", response_model=ReceiptResponse)
async def pay_bill(bill_id: int, data: PaymentRequest, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Bill).where(Bill.id == bill_id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    if bill.status == "paid":
        raise HTTPException(status_code=400, detail="Bill already paid")

    bill.status = "paid"
    bill.payment_method = data.payment_method.value
    bill.account_number = data.account_number
    bill.paid_date = datetime.utcnow()
    bill.receipt_ref = f"EP{datetime.utcnow().strftime('%y%m%d%H%M%S')}{bill.id}"

    await db.commit()
    await db.refresh(bill)

    method_labels = {"mpamba": "Mpamba", "airtel_money": "Airtel Money", "bank": "Bank Transfer"}
    method_label = method_labels.get(data.payment_method.value, data.payment_method.value)

    share_text = (
        f"eHealth Malawi Payment Receipt\n"
        f"Reference: {bill.receipt_ref}\n"
        f"Patient: {bill.patient_name}\n"
        f"Service: {bill.title}\n"
        f"Amount: MWK {bill.amount:,.2f}\n"
        f"Method: {method_label}\n"
        f"Account: {data.account_number}\n"
        f"Date: {bill.paid_date.strftime('%d %b %Y %H:%M')}\n"
    )

    return ReceiptResponse(
        receipt_ref=bill.receipt_ref,
        title=bill.title,
        amount=bill.amount,
        patient_name=bill.patient_name,
        payment_method=data.payment_method,
        account_number=data.account_number,
        paid_date=bill.paid_date,
        share_text=share_text,
    )


@router.delete("/bills/{bill_id}", status_code=204)
async def delete_bill(bill_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Bill).where(Bill.id == bill_id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    await db.delete(bill)
    await db.commit()


@router.put("/bills/{bill_id}", response_model=BillResponse)
async def update_bill(bill_id: int, data: BillUpdate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Bill).where(Bill.id == bill_id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bill, key, value)
    await db.commit()
    await db.refresh(bill)
    return bill
