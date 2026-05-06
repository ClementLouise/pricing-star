"""Pydantic schemas for Scenario + CountryData CRUD — per PRD §05."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


# ─── Regulations ────────────────────────────────────────────────────────────

class GenerousConfig(BaseModel):
    active: bool = False
    year: int | None = None
    medicaid_share: float = Field(0.07, ge=0, le=1)


class GuardConfig(BaseModel):
    active: bool = False
    year: int | None = None
    submit_method_ii: bool = False
    phase_in: float | None = None


class GlobeConfig(BaseModel):
    active: bool = False
    year: int | None = None
    submit_method_ii: bool = False
    phase_in: float | None = None


class RegulationsConfig(BaseModel):
    generous: GenerousConfig = GenerousConfig()
    guard: GuardConfig = GuardConfig()
    globe: GlobeConfig = GlobeConfig()


# ─── Levers ─────────────────────────────────────────────────────────────────

class LeversConfig(BaseModel):
    withdrawals: list[str] = []
    price_floors: dict[str, float] = {}
    delayed_launches: dict[str, int] = {}
    de_opt_in: bool = False
    gr_clawback_stress: bool = False


# ─── CountryData ─────────────────────────────────────────────────────────────

class CountryDataInput(BaseModel):
    list_price: float | None = Field(None, gt=0)
    net_price: float | None = Field(None, gt=0)
    volume: float | None = Field(None, ge=0, le=1)
    launched: bool = False
    launch_year: int | None = None
    withdrawn: bool = False
    g2n_ratio: float | None = Field(None, gt=0, le=1)
    g2n_time_series: dict[str, float] | None = None

    @model_validator(mode="after")
    def validate_g2n_time_series(self) -> "CountryDataInput":
        if self.g2n_time_series is None:
            return self
        for key, value in self.g2n_time_series.items():
            try:
                year = int(key)
            except (ValueError, TypeError):
                raise ValueError(f"G2N time series key '{key}' must be an integer year")
            if not (2020 <= year <= 2075):
                raise ValueError(f"G2N time series year {year} is out of range [2020, 2075]")
            if not (0 < value <= 1):
                raise ValueError(f"G2N time series value {value} for year {year} must be in (0, 1]")
        return self


class CountryDataRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    country_code: str
    list_price: float | None
    net_price: float | None
    volume: float | None
    launched: bool
    launch_year: int | None
    withdrawn: bool
    g2n_ratio: float | None
    g2n_time_series: dict | None


# ─── Scenario ────────────────────────────────────────────────────────────────

class ScenarioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    is_baseline: bool = False
    regulations: RegulationsConfig = RegulationsConfig()
    levers: LeversConfig = LeversConfig()
    cascade_config: dict = {}
    country_data: dict[str, CountryDataInput] = {}


class ScenarioUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_baseline: bool | None = None
    regulations: RegulationsConfig | None = None
    levers: LeversConfig | None = None
    cascade_config: dict | None = None


class ScenarioRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    asset_id: uuid.UUID
    name: str
    description: str | None
    is_baseline: bool
    regulations: dict
    levers: dict
    cascade_config: dict
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None


class ScenarioDuplicate(BaseModel):
    new_name: str = Field(..., min_length=1, max_length=255)
