from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.announcement import AnnouncementCategory, AnnouncementPriority


class AnnouncementCreate(BaseModel):
    title: str
    content: Optional[str] = None
    category: AnnouncementCategory = AnnouncementCategory.PUBLIC_HEALTH
    priority: AnnouncementPriority = AnnouncementPriority.MEDIUM
    facility_id: Optional[int] = None
    target_role: Optional[str] = None
    expiry_date: Optional[datetime] = None
    is_active: bool = True


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[AnnouncementCategory] = None
    priority: Optional[AnnouncementPriority] = None
    is_active: Optional[bool] = None
    expiry_date: Optional[datetime] = None


class AnnouncementResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    category: str
    priority: str
    facility_id: Optional[int] = None
    target_role: Optional[str] = None
    created_by: int
    is_active: bool
    expiry_date: Optional[datetime] = None
    read_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HealthIntelligence(BaseModel):
    malaria_cases_this_week: int = 0
    cholera_cases_this_week: int = 0
    vaccine_coverage_pct: float = 0
    facilities_online: int = 0
    pending_lab_samples: int = 0
    emergency_referrals: int = 0
    bed_occupancy_pct: float = 0
    dialysis_utilization_pct: float = 0
    blood_stock_units: int = 0


class SearchResult(BaseModel):
    type: str
    id: int
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
