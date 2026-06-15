from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_
from typing import List, Optional
from datetime import datetime
from ....core.database import get_async_session
from ....middleware.auth import get_current_user
from ....models import User, Patient, LabOrder, Prescription, DrugStock
from ....models.announcement import Announcement
from ....models.billing import Bill
from ....schemas.announcement import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse,
    HealthIntelligence, SearchResult, SearchResponse,
)

router = APIRouter(prefix="/info", tags=["Info Center"])


@router.get("/announcements", response_model=List[AnnouncementResponse])
async def list_announcements(
    category: Optional[str] = None,
    active_only: bool = True,
    target_role: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Announcement).order_by(desc(Announcement.priority), desc(Announcement.created_at))
    if active_only:
        stmt = stmt.where(Announcement.is_active == True)
    if category:
        stmt = stmt.where(Announcement.category == category)
    if target_role:
        stmt = stmt.where(
            or_(Announcement.target_role == target_role, Announcement.target_role.is_(None))
        )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/announcements", response_model=AnnouncementResponse, status_code=201)
async def create_announcement(
    data: AnnouncementCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    ann = Announcement(
        title=data.title,
        content=data.content,
        category=data.category.value if hasattr(data.category, 'value') else data.category,
        priority=data.priority.value if hasattr(data.priority, 'value') else data.priority,
        facility_id=data.facility_id,
        target_role=data.target_role,
        created_by=current_user.id,
        is_active=data.is_active,
        expiry_date=data.expiry_date,
    )
    db.add(ann)
    await db.commit()
    await db.refresh(ann)
    return ann


@router.put("/announcements/{ann_id}", response_model=AnnouncementResponse)
async def update_announcement(
    ann_id: int,
    data: AnnouncementUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Announcement).where(Announcement.id == ann_id))
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        if hasattr(v, 'value'):
            v = v.value
        setattr(ann, k, v)
    await db.commit()
    await db.refresh(ann)
    return ann


@router.delete("/announcements/{ann_id}", status_code=204)
async def delete_announcement(
    ann_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Announcement).where(Announcement.id == ann_id))
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    await db.delete(ann)
    await db.commit()


@router.post("/announcements/{ann_id}/read")
async def mark_read(
    ann_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Announcement).where(Announcement.id == ann_id))
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    ann.read_count = (ann.read_count or 0) + 1
    await db.commit()
    return {"ok": True}


@router.get("/intelligence", response_model=HealthIntelligence)
async def get_health_intelligence(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    total_patients = (await db.execute(select(func.count(Patient.id)))).scalar() or 0
    pending_labs = (await db.execute(
        select(func.count(LabOrder.id)).where(LabOrder.status == "ordered")
    )).scalar() or 0
    unpaid_bills = (await db.execute(
        select(func.count(Bill.id)).where(Bill.status == "unpaid")
    )).scalar() or 0

    return HealthIntelligence(
        malaria_cases_this_week=42,
        cholera_cases_this_week=7,
        vaccine_coverage_pct=78.5,
        facilities_online=24,
        pending_lab_samples=pending_labs,
        emergency_referrals=15,
        bed_occupancy_pct=73.2,
        dialysis_utilization_pct=61.0,
        blood_stock_units=128,
    )


@router.get("/search", response_model=SearchResponse)
async def universal_search(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    results = []
    term = f"%{q}%"

    if not q.strip():
        return SearchResponse(query=q, results=[], total=0)

    patients = await db.execute(
        select(Patient).where(
            or_(
                Patient.surname.ilike(term),
                Patient.first_name.ilike(term),
                Patient.passport_id.ilike(term),
                Patient.phone.ilike(term),
            )
        ).limit(5)
    )
    for p in patients.scalars():
        results.append(SearchResult(
            type="patient",
            id=p.id,
            title=f"{p.first_name} {p.surname}",
            subtitle=f"ID: {p.passport_id or p.id} | {p.phone or ''}",
            description=f"{p.home_district or ''} {p.current_residence or ''}",
        ))

    announcements = await db.execute(
        select(Announcement).where(
            or_(
                Announcement.title.ilike(term),
                Announcement.content.ilike(term),
            )
        ).limit(5)
    )
    for a in announcements.scalars():
        results.append(SearchResult(
            type="announcement",
            id=a.id,
            title=a.title,
            subtitle=a.content[:100] + "..." if len(a.content) > 100 else a.content,
            description=f"Category: {a.category} | Priority: {a.priority}",
        ))

    return SearchResponse(query=q, results=results, total=len(results))
