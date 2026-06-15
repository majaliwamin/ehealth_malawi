from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from ....core.database import get_async_session
from ....middleware.auth import get_current_user
from ....models import Patient, User
from ....schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientSearchResult

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/search", response_model=List[PatientSearchResult])
async def search_patients(
    query: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Patient).where(
        or_(
            Patient.surname.ilike(f"%{query}%"),
            Patient.first_name.ilike(f"%{query}%"),
            Patient.national_id.ilike(f"%{query}%"),
            Patient.passport_id.ilike(f"%{query}%"),
            Patient.file_number.ilike(f"%{query}%"),
            Patient.phone.ilike(f"%{query}%"),
        )
    ).limit(20)
    result = await db.execute(stmt)
    patients = result.scalars().all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/", response_model=PatientResponse, status_code=201)
async def create_patient(data: PatientCreate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    patient = Patient(**data.model_dump())
    patient.passport_id = f"EMW-{Patient.__tablename__}-{id(patient)}"
    db.add(patient)
    await db.flush()
    patient.passport_id = f"EMW-{str(patient.id).zfill(7)}"
    await db.commit()
    await db.refresh(patient)
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(patient_id: int, data: PatientUpdate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)
    await db.commit()
    await db.refresh(patient)
    return patient
