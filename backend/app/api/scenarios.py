"""Scenario + CountryData management endpoints — per PRD §05."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.database import get_db
from app.models.asset import Asset
from app.models.user import User
from app.repos.asset import AssetRepo
from app.repos.audit import AuditRepo
from app.repos.scenario import CountryDataRepo, ScenarioRepo
from app.schemas.scenario import (
    CountryDataInput,
    CountryDataRead,
    ScenarioCreate,
    ScenarioDuplicate,
    ScenarioRead,
    ScenarioUpdate,
)


def _assert_g2n_lifecycle(g2n_time_series: dict[str, float] | None, asset: Asset) -> None:
    """EC-CALC-13: reject g2n_time_series years outside [launch_year, loe_year + 5]."""
    if not g2n_time_series:
        return
    launch = asset.launch_year
    loe = asset.loe_year
    if launch is None or loe is None:
        return
    max_year = loe + 5
    for key in g2n_time_series:
        try:
            year = int(key)
        except (ValueError, TypeError):
            continue  # already caught by Pydantic
        if not (launch <= year <= max_year):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Year {year} is outside asset lifecycle [{launch}, {max_year}]",
            )

router = APIRouter(tags=["scenarios"])

_editor = require_role(["admin", "editor"])
_viewer = require_role(["admin", "editor", "viewer"])


# ─── Scenarios ────────────────────────────────────────────────────────────────

@router.get("/assets/{asset_id}/scenarios", response_model=list[ScenarioRead])
async def list_scenarios(
    asset_id: uuid.UUID,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> list[ScenarioRead]:
    asset = await AssetRepo(db).get(asset_id, user.tenant_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    items = await ScenarioRepo(db).list(asset_id, user.tenant_id)
    return [ScenarioRead.model_validate(s) for s in items]


@router.post("/assets/{asset_id}/scenarios", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    asset_id: uuid.UUID,
    payload: ScenarioCreate,
    user: User = Depends(_editor),
    db: AsyncSession = Depends(get_db),
) -> ScenarioRead:
    asset = await AssetRepo(db).get(asset_id, user.tenant_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    for cd_input in payload.country_data.values():
        _assert_g2n_lifecycle(cd_input.g2n_time_series, asset)

    scenario_repo = ScenarioRepo(db)
    scenario = await scenario_repo.create(asset_id, user.tenant_id, user.id, payload)

    if payload.country_data:
        await CountryDataRepo(db).bulk_create(scenario.id, user.tenant_id, payload.country_data)

    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="scenario.create",
        payload={"scenario_id": str(scenario.id), "asset_id": str(asset_id)},
    )
    return ScenarioRead.model_validate(scenario)


@router.get("/scenarios/{scenario_id}", response_model=ScenarioRead)
async def get_scenario(
    scenario_id: uuid.UUID,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> ScenarioRead:
    scenario = await ScenarioRepo(db).get(scenario_id, user.tenant_id)
    if scenario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return ScenarioRead.model_validate(scenario)


@router.patch("/scenarios/{scenario_id}", response_model=ScenarioRead)
async def update_scenario(
    scenario_id: uuid.UUID,
    payload: ScenarioUpdate,
    user: User = Depends(_editor),
    db: AsyncSession = Depends(get_db),
) -> ScenarioRead:
    repo = ScenarioRepo(db)
    scenario = await repo.get(scenario_id, user.tenant_id)
    if scenario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    scenario = await repo.update(scenario, payload)
    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="scenario.update",
        payload={"scenario_id": str(scenario_id)},
    )
    return ScenarioRead.model_validate(scenario)


@router.delete("/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_scenario(
    scenario_id: uuid.UUID,
    user: User = Depends(_editor),
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = ScenarioRepo(db)
    scenario = await repo.get(scenario_id, user.tenant_id)
    if scenario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    await repo.archive(scenario)
    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="scenario.archive",
        payload={"scenario_id": str(scenario_id)},
    )


@router.post("/scenarios/{scenario_id}/duplicate", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
async def duplicate_scenario(
    scenario_id: uuid.UUID,
    payload: ScenarioDuplicate,
    user: User = Depends(_editor),
    db: AsyncSession = Depends(get_db),
) -> ScenarioRead:
    repo = ScenarioRepo(db)
    scenario = await repo.get(scenario_id, user.tenant_id)
    if scenario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    clone = await repo.duplicate(scenario, payload.new_name, user.id)

    # Copy country data to cloned scenario
    cd_repo = CountryDataRepo(db)
    for cd in await cd_repo.list_for_scenario(scenario_id):
        await cd_repo.upsert(
            clone.id, user.tenant_id, cd.country_code,
            CountryDataInput(
                list_price=float(cd.list_price) if cd.list_price is not None else None,
                net_price=float(cd.net_price) if cd.net_price is not None else None,
                volume=float(cd.volume) if cd.volume is not None else None,
                launched=cd.launched,
                launch_year=cd.launch_year,
                withdrawn=cd.withdrawn,
                g2n_ratio=float(cd.g2n_ratio) if cd.g2n_ratio is not None else None,
                g2n_time_series=cd.g2n_time_series,
            ),
        )
    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="scenario.duplicate",
        payload={"source_id": str(scenario_id), "new_id": str(clone.id)},
    )
    return ScenarioRead.model_validate(clone)


# ─── Country data ─────────────────────────────────────────────────────────────

@router.get("/scenarios/{scenario_id}/country-data", response_model=list[CountryDataRead])
async def list_country_data(
    scenario_id: uuid.UUID,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> list[CountryDataRead]:
    scenario = await ScenarioRepo(db).get(scenario_id, user.tenant_id)
    if scenario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    items = await CountryDataRepo(db).list_for_scenario(scenario_id)
    return [CountryDataRead.model_validate(cd) for cd in items]


@router.patch("/scenarios/{scenario_id}/country-data/{country_code}", response_model=CountryDataRead)
async def upsert_country_data(
    scenario_id: uuid.UUID,
    country_code: str,
    payload: CountryDataInput,
    user: User = Depends(_editor),
    db: AsyncSession = Depends(get_db),
) -> CountryDataRead:
    scenario = await ScenarioRepo(db).get(scenario_id, user.tenant_id)
    if scenario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    asset = await AssetRepo(db).get(scenario.asset_id, user.tenant_id)
    if asset is not None:
        _assert_g2n_lifecycle(payload.g2n_time_series, asset)
    cd = await CountryDataRepo(db).upsert(scenario_id, user.tenant_id, country_code.upper(), payload)
    return CountryDataRead.model_validate(cd)


@router.delete("/scenarios/{scenario_id}/country-data/{country_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country_data(
    scenario_id: uuid.UUID,
    country_code: str,
    user: User = Depends(_editor),
    db: AsyncSession = Depends(get_db),
) -> None:
    scenario = await ScenarioRepo(db).get(scenario_id, user.tenant_id)
    if scenario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    cd_repo = CountryDataRepo(db)
    cd = await cd_repo.get(scenario_id, country_code.upper(), user.tenant_id)
    if cd is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country data not found")
    await cd_repo.delete(cd)
