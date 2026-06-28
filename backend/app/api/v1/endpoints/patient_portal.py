from fastapi import APIRouter, Depends, HTTPException, Header, status
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pydantic import BaseModel
from ....schemas.patient_portal import PatientRegister, PatientLogin, PatientToken, PatientUpdate

PATIENT_SECRET_KEY = "patient-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

router = APIRouter(prefix="", tags=["Patient Portal"])

class PayRequest(BaseModel):
    payment_method: str
    account_number: str
    pin_hash: str = ""
    amount: Optional[float] = None

# In-memory stores for demo
patients_db = {}
appointments_db = []
bills_db = []
lab_results_db = []
prescriptions_db = []
allergies_db = []
conditions_db = []
pending_bookings_db = []
notifications_db = []

_passport_counter = 2
_appointment_counter = 1

# Seed demo bills
_bill_id_counter = 0
def _seed_bills():
    global _bill_id_counter
    demo_bills = [
        {"title": "Consultation Fee", "description": "General consultation with Dr. Banda", "amount": 15000.0},
        {"title": "Lab Tests - Malaria & LFTs", "description": "Malaria rapid test and liver function tests", "amount": 8500.0},
        {"title": "Pharmacy - Antimalarials", "description": "Artemether-Lumefantrine course", "amount": 3200.0},
    ]
    for b in demo_bills:
        _bill_id_counter += 1
        bills_db.append({
            "id": _bill_id_counter,
            "patient_passport_id": "MHT-000001",
            "patient_name": "Demo Patient",
            "title": b["title"],
            "description": b["description"],
            "amount": b["amount"],
            "status": "unpaid",
            "payment_method": None,
            "account_number": None,
            "receipt_ref": None,
            "paid_date": None,
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=24 * _bill_id_counter)).isoformat(),
        })
_seed_bills()

# Seed demo patient
patients_db["MHT-000001"] = {
    "passport_id": "MHT-000001",
    "full_name": "Demo Patient",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "phone": "0999123456",
    "email": "demo.patient@example.com",
    "district": "Thyolo",
    "traditional_authority": "Kabudula",
    "village": "Demo Village",
    "occupation": "Farmer",
    "created_at": datetime.now(timezone.utc).isoformat(),
}

# Seed demo allergies
allergies_db.append({"id": 1, "patient_passport_id": "MHT-000001", "allergen": "Penicillin", "reaction": "Rash, hives", "severity": "moderate", "is_active": True})
allergies_db.append({"id": 2, "patient_passport_id": "MHT-000001", "allergen": "Peanuts", "reaction": "Swelling, difficulty breathing", "severity": "severe", "is_active": True})
allergies_db.append({"id": 3, "patient_passport_id": "MHT-000001", "allergen": "Latex", "reaction": "Contact dermatitis", "severity": "mild", "is_active": True})

# Seed demo appointment
appointments_db.append({
    "id": 1, "patient_passport_id": "MHT-000001", "patient_name": "Demo Patient",
    "appointment_date": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
    "appointment_type": "Follow-up", "department": "Internal Medicine",
    "reason": "Routine diabetes check-up", "status": "confirmed",
    "created_at": datetime.now(timezone.utc).isoformat(),
})

# Seed demo conditions (chronic)
conditions_db.append({"id": 1, "patient_passport_id": "MHT-000001", "diagnosis_name": "Type 2 Diabetes Mellitus", "icd_code": "E11", "diagnosis_type": "chronic", "is_chronic": True, "status": "managed", "onset_date": "2018-03-10", "notes": "Controlled with Metformin 500mg BID. Last HbA1c 6.8%", "is_active": True})
conditions_db.append({"id": 2, "patient_passport_id": "MHT-000001", "diagnosis_name": "Hypertension", "icd_code": "I10", "diagnosis_type": "chronic", "is_chronic": True, "status": "managed", "onset_date": "2019-07-22", "notes": "Controlled with Lisinopril 10mg daily. Last BP 128/82", "is_active": True})


def _create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, PATIENT_SECRET_KEY, algorithm=ALGORITHM)


def _decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, PATIENT_SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_patient(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    payload = _decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    passport_id = payload.get("sub")
    patient = patients_db.get(passport_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Patient not found")
    return patient


@router.post("/patient/register", response_model=PatientToken, status_code=201)
async def register(data: PatientRegister):
    global _passport_counter

    for p in patients_db.values():
        if p["phone"] == data.phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")

    passport_id = f"MHT-{_passport_counter:06d}"
    _passport_counter += 1

    patient = {
        "passport_id": passport_id,
        "full_name": data.full_name,
        "date_of_birth": data.date_of_birth,
        "gender": data.gender,
        "phone": data.phone,
        "email": data.email,
        "district": data.district,
        "traditional_authority": data.traditional_authority,
        "village": data.village,
        "occupation": data.occupation,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    patients_db[passport_id] = patient

    token = _create_access_token({"sub": passport_id, "role": "patient"})
    return PatientToken(access_token=token, user=patient)


@router.post("/patient/login", response_model=PatientToken)
async def login(data: PatientLogin):
    patient = patients_db.get(data.passport_id)
    if not patient or patient["phone"] != data.phone:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid passport ID or phone number")

    token = _create_access_token({"sub": data.passport_id, "role": "patient"})
    # Exclude sensitive fields from user dict in response
    return PatientToken(access_token=token, user=patient)


@router.get("/patient/profile")
async def get_profile(current_patient: dict = Depends(get_current_patient)):
    return current_patient


@router.put("/patient/profile")
async def update_profile(data: PatientUpdate, current_patient: dict = Depends(get_current_patient)):
    update_fields = data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        if value is not None:
            current_patient[key] = value
    patients_db[current_patient["passport_id"]] = current_patient
    return current_patient


@router.get("/patient/appointments")
async def get_appointments(current_patient: dict = Depends(get_current_patient)):
    return [a for a in appointments_db if a["patient_passport_id"] == current_patient["passport_id"]]


@router.post("/patient/appointments", status_code=201)
async def create_appointment(data: dict, current_patient: dict = Depends(get_current_patient)):
    global _appointment_counter
    appointment = {
        "id": _appointment_counter,
        "patient_passport_id": current_patient["passport_id"],
        "patient_name": current_patient["full_name"],
        "appointment_date": data.get("appointment_date"),
        "appointment_type": data.get("appointment_type"),
        "department": data.get("department"),
        "clinician_name": data.get("clinician_name"),
        "location": data.get("location"),
        "reason": data.get("reason"),
        "notes": data.get("notes"),
        "status": "pending",
        "priority": "routine",
        "is_teleconsult": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _appointment_counter += 1
    appointments_db.append(appointment)
    pending_bookings_db.append({
        "id": appointment["id"],
        "patient_passport_id": appointment["patient_passport_id"],
        "patient_name": appointment["patient_name"],
        "appointment_date": appointment["appointment_date"],
        "appointment_type": appointment["appointment_type"],
        "department": appointment["department"],
        "clinician_name": appointment["clinician_name"],
        "location": appointment["location"],
        "reason": appointment["reason"],
        "notes": appointment["notes"],
        "status": "pending",
        "created_at": appointment["created_at"],
        "notified": False,
    })
    return appointment


@router.get("/patient/bills")
async def get_bills(current_patient: dict = Depends(get_current_patient)):
    return [b for b in bills_db if b["patient_passport_id"] == current_patient["passport_id"]]


@router.post("/patient/bills/{bill_id}/pay")
async def pay_bill(bill_id: int, data: PayRequest, current_patient: dict = Depends(get_current_patient)):
    for b in bills_db:
        if b["id"] == bill_id and b["patient_passport_id"] == current_patient["passport_id"]:
            if b["status"] == "paid":
                raise HTTPException(status_code=400, detail="Bill already paid")
            paid_amount = data.amount if data.amount and data.amount > 0 else b["amount"]
            b["status"] = "paid"
            b["payment_method"] = data.payment_method
            b["account_number"] = data.account_number
            b["paid_amount"] = paid_amount
            b["paid_date"] = datetime.now(timezone.utc).isoformat()
            b["receipt_ref"] = f"RCP{datetime.now(timezone.utc).strftime('%y%m%d%H%M%S')}{bill_id}"
            method_labels = {"mpamba": "Mpamba", "airtel_money": "Airtel Money", "bank": "Bank Transfer"}
            return {
                "receipt_ref": b["receipt_ref"],
                "title": b["title"],
                "amount": paid_amount,
                "patient_name": b["patient_name"],
                "payment_method": data.payment_method,
                "account_number": data.account_number,
                "paid_date": b["paid_date"],
                "share_text": (
                    f"MUST Health Tech (MHT) — Payment Receipt\n"
                    f"Reference: {b['receipt_ref']}\n"
                    f"Patient: {b['patient_name']}\n"
                    f"Service: {b['title']}\n"
                    f"Amount: MWK {paid_amount:,.2f}\n"
                    f"Method: {method_labels.get(data.payment_method, data.payment_method)}\n"
                    f"Account: {data.account_number}\n"
                    f"Date: {datetime.now(timezone.utc).strftime('%d %b %Y %H:%M')}\n"
                ),
            }
    raise HTTPException(status_code=404, detail="Bill not found")


@router.get("/patient/results")
async def get_results(current_patient: dict = Depends(get_current_patient)):
    return [r for r in lab_results_db if r["patient_passport_id"] == current_patient["passport_id"]]


@router.get("/patient/prescriptions")
async def get_prescriptions(current_patient: dict = Depends(get_current_patient)):
    return [p for p in prescriptions_db if p["patient_passport_id"] == current_patient["passport_id"]]


@router.get("/patient/allergies")
async def get_allergies(current_patient: dict = Depends(get_current_patient)):
    return [a for a in allergies_db if a["patient_passport_id"] == current_patient["passport_id"] and a["is_active"]]


@router.get("/patient/conditions")
async def get_conditions(current_patient: dict = Depends(get_current_patient)):
    return [c for c in conditions_db if c["patient_passport_id"] == current_patient["passport_id"] and c["is_active"]]


# ===== PENDING BOOKINGS (clinician notification system) =====

@router.get("/patient/pending-bookings")
async def get_pending_bookings():
    return pending_bookings_db


@router.put("/patient/pending-bookings/{booking_id}/approve")
async def approve_booking(booking_id: int):
    for pb in pending_bookings_db:
        if pb["id"] == booking_id and pb["status"] == "pending":
            pb["status"] = "confirmed"
            pb["notified"] = True
            for a in appointments_db:
                if a["id"] == booking_id:
                    a["status"] = "confirmed"
                    break
            notifications_db.append({
                "id": len(notifications_db) + 1,
                "type": "booking_confirmed",
                "message": f"Appointment for {pb['patient_name']} on {pb['appointment_date']} confirmed",
                "patient_passport_id": pb["patient_passport_id"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "channel": "sms_whatsapp",
                "delivered": True,
            })
            return {"status": "confirmed", "message": f"Booking {booking_id} approved. Patient notified via SMS/WhatsApp."}
    raise HTTPException(status_code=404, detail="Pending booking not found")


@router.put("/patient/pending-bookings/{booking_id}/reject")
async def reject_booking(booking_id: int):
    for pb in pending_bookings_db:
        if pb["id"] == booking_id and pb["status"] == "pending":
            pb["status"] = "rejected"
            for a in appointments_db:
                if a["id"] == booking_id:
                    a["status"] = "cancelled"
                    break
            return {"status": "rejected", "message": f"Booking {booking_id} rejected."}
    raise HTTPException(status_code=404, detail="Pending booking not found")


@router.get("/patient/notifications")
async def get_notifications():
    return notifications_db
