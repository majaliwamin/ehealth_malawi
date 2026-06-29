from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime
from ....core.database import get_async_session
from ....middleware.auth import get_current_user
from ....models import LabOrder, LabTest, User
from ....schemas.laboratory import (LabOrderCreate, LabResultUpdate, LabOrderResponse,
                                    AIInterpretRequest, AIInterpretResponse,
                                    AIParseTextRequest, AIParseTextResponse,
                                    AITestGuideRequest, AITestGuideResponse)
from ....services.lab_ai import interpret_batch, DEPARTMENT_TESTS, parse_free_text, get_test_procedure
from ....services.ocr_service import ocr_image

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


@router.post("/ai-interpret", response_model=AIInterpretResponse)
async def ai_interpret_results(data: AIInterpretRequest):
    result = interpret_batch(
        results=data.tests,
        gender=data.gender,
        age=data.age,
        pregnant=data.pregnant,
        patient_name=data.patient_name or "",
        metadata={"patient_id": data.patient_id} if data.patient_id else None,
    )
    return result


@router.get("/ai-tests")
async def list_ai_tests():
    """Return all tests grouped by department for frontend dropdowns."""
    return {dept: [{"name": t.name, "unit": t.unit} for t in tests]
            for dept, tests in DEPARTMENT_TESTS.items()}


@router.post("/ai-parse-text", response_model=AIParseTextResponse)
async def ai_parse_text_results(data: AIParseTextRequest):
    """Parse free text lab results and return AI interpretations."""
    result = parse_free_text(
        text=data.text,
        gender=data.gender,
        age=data.age,
        pregnant=data.pregnant,
        patient_name=data.patient_name or "",
        patient_id=data.patient_id,
    )
    return result


@router.post("/ai-test-guide", response_model=AITestGuideResponse)
async def ai_test_procedure_guide(data: AITestGuideRequest):
    """Return full procedure guide for a given test (pre-analytical → post-analytical)."""
    guide = get_test_procedure(data.test_name)
    if not guide:
        raise HTTPException(status_code=404, detail=f"Test '{data.test_name}' not found in procedure knowledge base.")
    return guide


@router.post("/ai-ocr-interpret")
async def ai_ocr_interpret(
    file: UploadFile = File(...),
    gender: str = Form("male"),
    age: Optional[float] = Form(None),
    pregnant: bool = Form(False),
    patient_name: str = Form(""),
    lang: str = Form("eng"),
):
    """Upload a lab result image/scan, run OCR, then interpret results."""
    if not file.content_type or not file.content_type.startswith(("image/", "application/pdf")):
        raise HTTPException(status_code=400, detail="Only image files (JPEG, PNG) and PDF are supported.")

    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 20 MB.")

    ocr_result = ocr_image(contents, lang=lang)

    if not ocr_result["success"] or not ocr_result.get("text"):
        return {
            "success": False,
            "engine_used": ocr_result.get("engine_used"),
            "error": ocr_result.get("error", "OCR could not extract any text from the image."),
            "extracted_text": None,
            "results": [],
            "summary": "OCR failed to extract text. Try a clearer image or enter results manually.",
            "total_tests": 0,
            "abnormal_count": 0,
        }

    extracted_text = ocr_result["text"]
    interpretation = parse_free_text(
        text=extracted_text,
        gender=gender,
        age=age,
        pregnant=pregnant,
        patient_name=patient_name,
    )

    return {
        "success": True,
        "engine_used": ocr_result["engine_used"],
        "extracted_text": extracted_text,
        "patient": interpretation["patient"],
        "gender": interpretation["gender"],
        "age": interpretation["age"],
        "pregnant": interpretation["pregnant"],
        "results": interpretation["results"],
        "summary": interpretation["summary"],
        "total_tests": interpretation["total_tests"],
        "abnormal_count": interpretation["abnormal_count"],
    }
