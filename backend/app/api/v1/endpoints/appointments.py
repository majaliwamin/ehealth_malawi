from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from typing import List, Optional
from datetime import datetime, date
from ....core.database import get_async_session
from ....middleware.auth import get_current_user
from ....models import Appointment, Queue, AppointmentStatus, User, Patient, NotificationChannel
from ....schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse, QueueResponse
from ....services.notification_service import NotificationService

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(data: AppointmentCreate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    appointment = Appointment(**data.model_dump())
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Appointment).order_by(desc(Appointment.appointment_date)))
    return result.scalars().all()


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(appointment_id: int, data: AppointmentUpdate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(appointment, key, value)
    await db.commit()
    await db.refresh(appointment)

    if data.status == AppointmentStatus.CONFIRMED:
        patient_result = await db.execute(select(Patient).where(Patient.id == appointment.patient_id))
        patient = patient_result.scalar_one_or_none()
        if patient and patient.phone:
            date_str = appointment.appointment_date.strftime("%A, %d %B %Y at %I:%M %p") if appointment.appointment_date else "the scheduled date"
            msg = (
                f"Dear {patient.first_name}, your appointment at MUST Teaching Hospital "
                f"has been confirmed for {date_str}. "
                f"Type: {appointment.appointment_type}. "
                f"Please carry your passport ID. Reply STOP to opt out."
            )
            try:
                await NotificationService.notify(
                    db=db,
                    phone=patient.phone,
                    message=msg,
                    channel=NotificationChannel.WHATSAPP,
                    patient_id=patient.id,
                    user_id=current_user.id,
                    template="booking_confirmed",
                )
            except Exception:
                pass

    return appointment


@router.put("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(appointment_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.status != AppointmentStatus.SCHEDULED:
        raise HTTPException(status_code=400, detail="Only scheduled appointments can be confirmed")
    appointment.status = AppointmentStatus.CONFIRMED
    await db.commit()
    await db.refresh(appointment)
    patient_result = await db.execute(select(Patient).where(Patient.id == appointment.patient_id))
    patient = patient_result.scalar_one_or_none()
    if patient and patient.phone:
        date_str = appointment.appointment_date.strftime("%A, %d %B %Y at %I:%M %p") if appointment.appointment_date else "the scheduled date"
        msg = (
            f"Dear {patient.first_name}, your appointment at MUST Teaching Hospital "
            f"has been confirmed for {date_str}. "
            f"Type: {appointment.appointment_type}. "
            f"Please carry your passport ID. Reply STOP to opt out."
        )
        try:
            await NotificationService.notify(
                db=db, phone=patient.phone, message=msg,
                channel=NotificationChannel.WHATSAPP, patient_id=patient.id,
                user_id=current_user.id, template="booking_confirmed",
            )
        except Exception:
            pass
    return appointment


@router.put("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(appointment_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Appointment is already cancelled")
    appointment.status = AppointmentStatus.CANCELLED
    await db.commit()
    await db.refresh(appointment)
    return appointment


@router.put("/{appointment_id}/reinstate", response_model=AppointmentResponse)
async def reinstate_appointment(appointment_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.status != AppointmentStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Only cancelled appointments can be reinstated")
    appointment.status = AppointmentStatus.SCHEDULED
    await db.commit()
    await db.refresh(appointment)
    return appointment


@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
async def get_patient_appointments(patient_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Appointment).where(Appointment.patient_id == patient_id).order_by(desc(Appointment.appointment_date))
    )
    return result.scalars().all()


@router.get("/today/upcoming", response_model=List[AppointmentResponse])
async def get_today_appointments(db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.appointment_date >= today_start,
                Appointment.appointment_date <= today_end,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
            )
        ).order_by(Appointment.appointment_date)
    )
    return result.scalars().all()


@router.get("/queue/", response_model=List[QueueResponse])
async def get_queue(department: Optional[str] = None, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    stmt = select(Queue)
    if department:
        stmt = stmt.where(Queue.department == department)
    stmt = stmt.order_by(Queue.position)
    result = await db.execute(stmt)
    return result.scalars().all()
