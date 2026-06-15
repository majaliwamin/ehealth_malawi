from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Date, Enum as SAEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class InventoryCategory(enum.Enum):
    MEDICATION = "medication"
    SUPPLIES = "supplies"
    EQUIPMENT = "equipment"
    LAB_REAGENT = "lab_reagent"
    PPE = "ppe"
    LINEN = "linen"
    INSTRUMENT = "instrument"
    OTHER = "other"


class StockMovementType(enum.Enum):
    RECEIVED = "received"
    DISPENSED = "dispensed"
    TRANSFERRED_IN = "transferred_in"
    TRANSFERRED_OUT = "transferred_out"
    ADJUSTED = "adjusted"
    EXPIRED = "expired"
    DAMAGED = "damaged"
    RETURNED = "returned"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(50), unique=True, nullable=True)
    item_name = Column(String(300), nullable=False)
    category = Column(SAEnum(InventoryCategory), nullable=False)
    description = Column(Text, nullable=True)
    unit_of_measure = Column(String(50), nullable=True)
    unit_cost = Column(Float, nullable=True)
    supplier = Column(String(200), nullable=True)
    manufacturer = Column(String(200), nullable=True)

    current_stock = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    maximum_stock = Column(Integer, nullable=True)

    storage_location = Column(String(100), nullable=True)
    shelf = Column(String(50), nullable=True)
    bin = Column(String(50), nullable=True)

    requires_refrigeration = Column(Boolean, default=False)
    is_controlled = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    last_count_date = Column(DateTime(timezone=True), nullable=True)
    last_count_quantity = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    movement_type = Column(SAEnum(StockMovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)
    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(Date, nullable=True)

    reference_type = Column(String(100), nullable=True)
    reference_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    performed_by = Column(Integer, nullable=False)
    performed_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("InventoryItem")


class EquipmentMaintenance(Base):
    __tablename__ = "equipment_maintenance"

    id = Column(Integer, primary_key=True, index=True)
    equipment_name = Column(String(300), nullable=False)
    equipment_code = Column(String(50), nullable=True)
    serial_number = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    manufacturer = Column(String(200), nullable=True)

    maintenance_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    performed_by = Column(String(200), nullable=True)
    performed_at = Column(DateTime(timezone=True), nullable=True)
    next_due_date = Column(Date, nullable=True)
    cost = Column(Float, nullable=True)

    status = Column(String(50), default="operational")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
