from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime
from ....core.database import get_async_session
from ....middleware.auth import get_current_user
from ....models import LabOrder, LabTest, User
from ....schemas.laboratory import LabOrderCreate, LabResultUpdate, LabOrderResponse

router = APIRouter(prefix="/labs", tags=["Laboratory"])


@router.post("/orders", response_model=LabOrderResponse, status_code=201)
async def create_lab_order(data: LabOrderCreate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    order = LabOrder(**data.model_dump())
    order.order_number = f"LAB-{datetime.now().strftime('%Y%m%d')}-{id(order)}"
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


@router.get("/orders/{order_id}", response_model=LabOrderResponse)
async def get_lab_order(order_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(LabOrder).where(LabOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Lab order not found")
    return order


@router.get("/orders/patient/{patient_id}", response_model=List[LabOrderResponse])
async def get_patient_lab_orders(patient_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(LabOrder).where(LabOrder.patient_id == patient_id).order_by(desc(LabOrder.created_at))
    )
    return result.scalars().all()


@router.get("/pending", response_model=List[LabOrderResponse])
async def get_pending_orders(db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(LabOrder).where(LabOrder.status == "ordered").order_by(desc(LabOrder.created_at))
    )
    return result.scalars().all()


@router.put("/orders/{order_id}/results", response_model=LabOrderResponse)
async def update_lab_results(order_id: int, data: LabResultUpdate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(LabOrder).where(LabOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Lab order not found")

    order.status = data.status
    order.result_notes = data.result_notes
    order.verified_by = current_user.id
    order.verified_at = datetime.now()

    # Remove existing tests and replace
    existing = await db.execute(select(LabTest).where(LabTest.order_id == order_id))
    for t in existing.scalars().all():
        await db.delete(t)

    for test_data in data.tests:
        test = LabTest(order_id=order_id, **test_data.model_dump())
        test.performed_by = current_user.id
        test.performed_at = datetime.now()
        if test.result_value or test.result_text:
            test.is_abnormal = False
        db.add(test)

    await db.commit()
    await db.refresh(order)
    return order
