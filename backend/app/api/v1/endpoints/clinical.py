from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from ....core.database import get_async_session
from ....middleware.auth import get_current_user
from ....models import Visit, VitalSign, ClinicalNote, VisitStatus, User
from ....schemas.clinical import VisitCreate, VisitResponse, VitalSignCreate, VitalSignResponse, ClinicalNoteCreate, ClinicalNoteResponse

router = APIRouter(prefix="/clinical", tags=["Clinical"])


@router.post("/visits", response_model=VisitResponse, status_code=201)
async def create_visit(data: VisitCreate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    visit = Visit(**data.model_dump())
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    return visit


@router.get("/visits/{visit_id}", response_model=VisitResponse)
async def get_visit(visit_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Visit).where(Visit.id == visit_id))
    visit = result.scalar_one_or_none()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit


@router.get("/visits/patient/{patient_id}", response_model=List[VisitResponse])
async def get_patient_visits(patient_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Visit).where(Visit.patient_id == patient_id).order_by(desc(Visit.visit_date))
    )
    return result.scalars().all()


@router.get("/visits/active", response_model=List[VisitResponse])
async def get_active_visits(db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Visit).where(
            Visit.status.in_([VisitStatus.WAITING, VisitStatus.IN_CONSULTATION, VisitStatus.ADMITTED])
        ).order_by(desc(Visit.visit_date))
    )
    return result.scalars().all()


@router.post("/vitals", response_model=VitalSignResponse, status_code=201)
async def record_vitals(data: VitalSignCreate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    vitals = VitalSign(**data.model_dump())
    if vitals.height_cm and vitals.height_cm > 0 and vitals.weight_kg and vitals.weight_kg > 0:
        vitals.bmi = round(vitals.weight_kg / ((vitals.height_cm / 100) ** 2), 1)
    db.add(vitals)
    await db.commit()
    await db.refresh(vitals)
    return vitals


@router.get("/vitals/{patient_id}", response_model=List[VitalSignResponse])
async def get_patient_vitals(patient_id: int, limit: int = 20, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(VitalSign).where(VitalSign.patient_id == patient_id).order_by(desc(VitalSign.recorded_at)).limit(limit)
    )
    return result.scalars().all()


@router.post("/notes", response_model=ClinicalNoteResponse, status_code=201)
async def create_clinical_note(data: ClinicalNoteCreate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    note = ClinicalNote(**data.model_dump(), created_by=0)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/notes/{patient_id}", response_model=List[ClinicalNoteResponse])
async def get_patient_notes(patient_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(ClinicalNote).where(ClinicalNote.patient_id == patient_id).order_by(desc(ClinicalNote.created_at))
    )
    return result.scalars().all()
