from datetime import datetime
from decimal import Decimal
from typing import Optional
import re
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ============================================================================
# 1. STUDENT SCHEMAS
# ============================================================================

class StudentBase(BaseModel):
    reg_no: str = Field(..., example="25BCE0750", description="Institutional Registration Number")
    name: str = Field(..., min_length=2, max_length=100, example="Rajveer Modi")
    email: str = Field(..., example="rajveer.modi2025@vitstudent.ac.in")

    @field_validator("reg_no")
    def validate_registration_number(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.match(r"^[0-9]{2}[A-Z]{3}[0-9]{4}$", v):
            raise ValueError("Registration number must follow standard format (e.g., 25BCE0750)")
        return v

    @field_validator("email")
    def validate_institutional_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[A-Za-z0-9._%+-]+@vitstudent\.ac\.in$", v):
            raise ValueError("Email must be an authorized campus address ending in @vitstudent.ac.in")
        return v


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    trust_rating: Decimal = Field(..., ge=1.00, le=5.00)
    balance: Decimal = Field(..., ge=0.00)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 2. TASK SCHEMAS
# ============================================================================

class TaskCreate(BaseModel):
    requester_id: str = Field(..., example="25BCE0750")
    pickup_location: str = Field(..., min_length=3, max_length=100, example="Food Mall Ground Floor")
    drop_location: str = Field(..., min_length=3, max_length=100, example="Technology Tower (TT) 412")
    bounty: Decimal = Field(..., gt=0.00, decimal_places=2, example=60.00)
    verification_pin: str = Field(..., min_length=4, max_length=4, example="4821")

    @field_validator("verification_pin")
    def validate_pin_format(cls, v: str) -> str:
        if not re.match(r"^[0-9]{4}$", v):
            raise ValueError("Verification PIN must be exactly 4 numeric digits")
        return v


class TaskFeedResponse(BaseModel):
    """
    Public task response matching Active_Open_Tasks_View.
    Crucially omits verification_pin and requester_id balances for privacy.
    """
    task_id: int
    pickup_location: str
    drop_location: str
    bounty: Decimal
    requester_name: str
    requester_rating: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskHandoverVerify(BaseModel):
    """Schema for runners submitting completion PIN at drop-off."""
    runner_id: str = Field(..., example="25BCE0717")
    verification_pin: str = Field(..., min_length=4, max_length=4, example="4821")


# ============================================================================
# 3. BID SCHEMAS
# ============================================================================

class BidCreate(BaseModel):
    task_id: int = Field(..., gt=0)
    runner_id: str = Field(..., example="25BCE0724")


class BidResponse(BaseModel):
    bid_id: int
    task_id: int
    runner_id: str
    offered_time: datetime
    bid_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)