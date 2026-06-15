from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models import LabOrderStatus, SpecimenType


class LabOrderCreate(BaseModel):
    patient_id: int
    visit_id: Optional[int] = None
    clinician_id: Optional[int] = None
    clinical_indication: Optional[str] = None
    diagnosis_code: Optional[str] = None
    is_urgent: bool = False
    specimen_type: Optional[SpecimenType] = None


class LabTestResult(BaseModel):
    test_name: str
    test_code: Optional[str] = None
    result_value: Optional[str] = None
    result_unit: Optional[str] = None
    reference_range_low: Optional[str] = None
    reference_range_high: Optional[str] = None
    result_text: Optional[str] = None
    result_qualitative: Optional[str] = None


class LabResultUpdate(BaseModel):
    tests: List[LabTestResult]
    result_notes: Optional[str] = None
    status: LabOrderStatus = LabOrderStatus.COMPLETED


class LabOrderResponse(BaseModel):
    id: int
    patient_id: int
    order_number: Optional[str] = None
    clinician_name: Optional[str] = None
    clinical_indication: Optional[str] = None
    is_urgent: bool
    specimen_type: Optional[SpecimenType] = None
    status: LabOrderStatus
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
