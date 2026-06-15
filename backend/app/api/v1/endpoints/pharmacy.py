from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime
from ....core.database import get_async_session
from ....middleware.auth import get_current_user
from ....models import Prescription, PrescriptionItem, PrescriptionStatus, User
from ....schemas.pharmacy import PrescriptionCreate, DispenseRequest, PrescriptionResponse

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy"])


@router.post("/prescriptions", response_model=PrescriptionResponse, status_code=201)
async def create_prescription(data: PrescriptionCreate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    items_data = data.items
    prescription = Prescription(
        patient_id=data.patient_id,
        visit_id=data.visit_id,
        prescribed_by_name=data.prescribed_by_name,
        diagnosis_code=data.diagnosis_code,
        clinical_indication=data.clinical_indication,
        notes=data.notes,
        is_emergency=data.is_emergency,
    )
    prescription.prescription_number = f"RX-{datetime.now().strftime('%Y%m%d')}-{id(prescription)}"
    db.add(prescription)
    await db.flush()

    for item_data in items_data:
        item = PrescriptionItem(
            prescription_id=prescription.id,
            **item_data.model_dump()
        )
        db.add(item)

    await db.commit()
    await db.refresh(prescription)
    return prescription


@router.get("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(prescription_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Prescription).where(Prescription.id == prescription_id))
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription


@router.get("/prescriptions/patient/{patient_id}", response_model=List[PrescriptionResponse])
async def get_patient_prescriptions(patient_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Prescription).where(Prescription.patient_id == patient_id).order_by(desc(Prescription.created_at))
    )
    return result.scalars().all()


@router.put("/prescriptions/{prescription_id}/dispense", response_model=PrescriptionResponse)
async def dispense_prescription(prescription_id: int, data: DispenseRequest, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Prescription).where(Prescription.id == prescription_id))
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    prescription.status = data.status
    prescription.dispensed_by = current_user.id
    prescription.dispensed_at = datetime.now()
    prescription.dispense_notes = data.dispense_notes

    await db.commit()
    await db.refresh(prescription)
    return prescription
