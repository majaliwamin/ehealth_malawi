"""Seed sample data for eHealth Malawi platform."""
import asyncio
import sys
sys.path.insert(0, ".")
from app.core.database import init_db, AsyncSessionLocal
from app.core.security import hash_password
from app.models import User, UserRole, Patient, Gender, Department, Facility
from app.models.billing import Bill
from app.models.announcement import Announcement
from datetime import date, datetime, timedelta


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        admin = User(
            username="ehealth_mw",
            email="admin@ehealth.mw",
            hashed_password=hash_password("must@ghs"),
            surname="System",
            first_name="Admin",
            role=UserRole.SUPER_ADMIN,
            designation="Platform Administrator",
            facility="Kamuzu Central Hospital",
            district="Lilongwe",
            is_verified=True,
            requires_password_change=False,
        )
        db.add(admin)

        doctor = User(
            username="doctor1",
            email="doctor@ehealth.mw",
            hashed_password=hash_password("Doctor@123"),
            surname="Banda",
            first_name="John",
            role=UserRole.DOCTOR,
            designation="Senior Medical Officer",
            department="Internal Medicine",
            facility="Kamuzu Central Hospital",
            district="Lilongwe",
            license_number="MMC-2024-001",
            is_verified=True,
            requires_password_change=False,
        )
        db.add(doctor)

        nurse = User(
            username="nurse1",
            email="nurse@ehealth.mw",
            hashed_password=hash_password("Nurse@123"),
            surname="Phiri",
            first_name="Grace",
            role=UserRole.NURSE,
            designation="Registered Nurse",
            department="Ward 3A",
            facility="Kamuzu Central Hospital",
            district="Lilongwe",
            is_verified=True,
            requires_password_change=False,
        )
        db.add(nurse)

        patient = Patient(
            passport_id="EMW-0000001",
            surname="Jameson",
            first_name="Sarah",
            date_of_birth=date(1994, 3, 15),
            gender=Gender.FEMALE,
            blood_group="O+",
            phone="+265 888 123 456",
            home_district="Nkhotakota",
            traditional_authority="Mwansambo",
            village="Chombe",
            current_residence="Area 47, Lilongwe",
            emergency_contact_name="Peter Jameson",
            emergency_contact_relation="Spouse",
            emergency_contact_phone="+265 999 789 012",
        )
        db.add(patient)

        patient2 = Patient(
            passport_id="EMW-0000002",
            surname="Banda",
            first_name="Chifundo",
            date_of_birth=date(1988, 7, 22),
            gender=Gender.MALE,
            blood_group="A+",
            phone="+265 999 456 789",
            home_district="Dedza",
            traditional_authority="Kachere",
            village="Mkosa",
            current_residence="Area 25, Lilongwe",
        )
        db.add(patient2)

        dept = Department(
            name="Internal Medicine", code="IM", facility="Kamuzu Central Hospital", head_of_department=2
        )
        db.add(dept)

        facility = Facility(
            name="Kamuzu Central Hospital", code="KCH", type="Central Hospital",
            district="Lilongwe", region="Central", level="referral", bed_capacity=950,
            phone="+265 1 756 244", email="info@kch.mw"
        )
        db.add(facility)

        bill1 = Bill(
            title="Consultation Fee",
            description="Outpatient consultation with Dr. John Banda",
            amount=15000.00,
            patient_id=1,
            patient_name="Sarah Jameson",
            patient_phone="+265 888 123 456",
            created_by=1,
            status="unpaid",
        )
        db.add(bill1)

        bill2 = Bill(
            title="Laboratory Services - Full Blood Count",
            description="FBC, Malaria RDT, Blood Glucose",
            amount=8500.00,
            patient_id=1,
            patient_name="Sarah Jameson",
            patient_phone="+265 888 123 456",
            created_by=1,
            status="paid",
            payment_method="mpamba",
            account_number="0999 123 456",
            receipt_ref="EP240612001",
            paid_date=datetime(2026, 6, 12, 10, 30),
        )
        db.add(bill2)

        bill3 = Bill(
            title="Pharmacy - Amoxicillin 500mg",
            description="Amoxicillin 500mg x 21 capsules",
            amount=3200.00,
            patient_id=2,
            patient_name="Chifundo Banda",
            patient_phone="+265 999 456 789",
            created_by=1,
            status="unpaid",
        )
        db.add(bill3)

        now = datetime.utcnow()
        announcements = [
            Announcement(title="Cholera Outbreak Alert — Lilongwe District", content="Three confirmed cholera cases reported in Area 25. All facilities to activate diarrhoeal disease surveillance and ensure adequate ORS and zinc stocks. Report suspected cases immediately to District Health Office.", category="critical", priority="high", created_by=1),
            Announcement(title="Malaria Surveillance Update — Week 24", content="Malaria incidence up 18% compared to same period last year. 42 confirmed cases this week in Central Region. Ensure RDT stock levels maintained and severe malaria protocols followed.", category="public_health", priority="high", created_by=1),
            Announcement(title="Dialysis Services Available — KCH Renal Unit", content="Kamuzu Central Hospital Renal Unit has resumed full dialysis services. All 12 hemodialysis machines operational. Emergency dialysis referrals accepted 24/7.", category="service", priority="medium", created_by=1),
            Announcement(title="CT Scan Available — Queen Elizabeth Central Hospital", content="QECH CT scanner back online following maintenance. Urgent scans prioritized. Contact Radiology Department for scheduling at +265 1 876 322.", category="service", priority="medium", created_by=1),
            Announcement(title="Measles Vaccination Campaign", content="National measles-rubella vaccination campaign launching July 1–14, 2026. Target: all children 6–59 months. Outreach teams will cover hard-to-reach areas. Vaccine stock pre-positioned at all district cold chain points.", category="public_health", priority="medium", created_by=1),
            Announcement(title="ICU Bed Availability — National Report", content="Current ICU occupancy: 73%. Available beds: KCH (4), QECH (2), Mwaiwathu (1), Kamuzu Central (0). Contact bed management for transfers.", category="service", priority="medium", created_by=1),
            Announcement(title="Staff Training Schedule — July 2026", content="EMR Advanced Training: July 5–9 (Lilongwe). Emergency Triage: July 12–16 (Blantyre). Lab Quality Management: July 19–23 (Mzuzu). Register via HR portal.", category="admin", priority="low", created_by=1),
            Announcement(title="Blood Bank Status — National", content="Current stocks: O+ (48 units), A+ (32), B+ (21), AB+ (8), O- (12), A- (5). Urgently need O- and B- donations. Mobile blood drive at Bingu Stadium this Saturday.", category="service", priority="medium", created_by=1),
            Announcement(title="System Maintenance Notice — July 2", content="Planned system maintenance: Saturday July 2, 22:00–04:00. The EMR system will be intermittently unavailable. Please ensure all patient records are saved before 22:00.", category="admin", priority="low", created_by=1),
            Announcement(title="Ambulance Availability Alert", content="National ambulance fleet status: 18 ambulances available, 6 on call, 3 undergoing maintenance. Central Region has 4 standby. Dedicated maternal transport: 2 ambulances on standby.", category="service", priority="medium", created_by=1),
        ]
        for a in announcements:
            db.add(a)

        await db.commit()
        print("Seed data created successfully!")
        print("Admin login: ehealth_mw / must@ghs")
        print("Doctor login: doctor1 / Doctor@123")
        print("Nurse login: nurse1 / Nurse@123")
        print("Patients: Sarah Jameson (EMW-0000001), Chifundo Banda (EMW-0000002)")
        print("Sample bills: Consultation (MWK 15,000 unpaid), Lab FBC (MWK 8,500 paid), Pharmacy (MWK 3,200 unpaid)")
        print("Announcements seeded: 10")


if __name__ == "__main__":
    asyncio.run(seed())
