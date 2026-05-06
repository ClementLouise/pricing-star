"""Pydantic schemas for Asset CRUD — per PRD §05."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class AssetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    therapeutic_area: str | None = None
    modality: str | None = None
    indication: str | None = None
    us_list_price: float | None = Field(None, gt=0)
    us_net_share: float | None = Field(None, ge=0, le=1)
    launch_year: int | None = Field(None, ge=2020, le=2060)
    peak_year: int | None = Field(None, ge=2020, le=2060)
    loe_year: int | None = Field(None, ge=2020, le=2070)
    cogs_percent: float = Field(0.15, ge=0, le=1)
    discount_rate: float = Field(0.10, ge=0, le=1)
    us_patient_population: int | None = Field(None, gt=0)
    ex_us_patient_population: int | None = Field(None, gt=0)
    peak_capture_rate: float = Field(0.5, ge=0, le=1)
    part_b_share: float = Field(0.5, ge=0, le=1)
    ramp_years: int = Field(4, ge=1, le=15)

    @model_validator(mode="after")
    def validate_year_ordering(self) -> "AssetCreate":
        if self.loe_year and self.launch_year and self.loe_year <= self.launch_year:
            raise ValueError("loe_year must be after launch_year")
        if self.peak_year and self.launch_year and self.peak_year < self.launch_year:
            raise ValueError("peak_year must be >= launch_year")
        if self.peak_year and self.loe_year and self.peak_year >= self.loe_year:
            raise ValueError("peak_year must be before loe_year")
        return self


class AssetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    therapeutic_area: str | None = None
    modality: str | None = None
    indication: str | None = None
    us_list_price: float | None = Field(None, gt=0)
    us_net_share: float | None = Field(None, ge=0, le=1)
    launch_year: int | None = None
    peak_year: int | None = None
    loe_year: int | None = None
    cogs_percent: float | None = Field(None, ge=0, le=1)
    discount_rate: float | None = Field(None, ge=0, le=1)
    us_patient_population: int | None = None
    ex_us_patient_population: int | None = None
    peak_capture_rate: float | None = Field(None, ge=0, le=1)
    part_b_share: float | None = Field(None, ge=0, le=1)
    ramp_years: int | None = Field(None, ge=1, le=15)


class AssetRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    therapeutic_area: str | None
    modality: str | None
    indication: str | None
    us_list_price: float | None
    us_net_share: float | None
    launch_year: int | None
    peak_year: int | None
    loe_year: int | None
    cogs_percent: float
    discount_rate: float
    us_patient_population: int | None
    ex_us_patient_population: int | None
    peak_capture_rate: float
    part_b_share: float
    ramp_years: int
    is_sample: bool
    sample_origin: str | None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None


class AssetDuplicate(BaseModel):
    new_name: str = Field(..., min_length=1, max_length=255)
