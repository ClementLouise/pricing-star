"""Scenario + CountryData repositories — every query filters by tenant_id per PRD §03."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.country_data import CountryData
from app.models.scenario import Scenario
from app.schemas.scenario import CountryDataInput, ScenarioCreate, ScenarioUpdate


class ScenarioRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list(
        self,
        asset_id: uuid.UUID,
        tenant_id: uuid.UUID,
        include_archived: bool = False,
    ) -> list[Scenario]:
        q = select(Scenario).where(
            Scenario.asset_id == asset_id,
            Scenario.tenant_id == tenant_id,
        )
        if not include_archived:
            q = q.where(Scenario.archived_at.is_(None))
        q = q.order_by(Scenario.created_at.desc())
        result = await self._db.execute(q)
        return list(result.scalars().all())

    async def get(self, scenario_id: uuid.UUID, tenant_id: uuid.UUID) -> Scenario | None:
        result = await self._db.execute(
            select(Scenario).where(
                Scenario.id == scenario_id,
                Scenario.tenant_id == tenant_id,
                Scenario.archived_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        asset_id: uuid.UUID,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: ScenarioCreate,
    ) -> Scenario:
        scenario = Scenario(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            asset_id=asset_id,
            created_by=user_id,
            name=payload.name,
            description=payload.description,
            is_baseline=payload.is_baseline,
            regulations=payload.regulations.model_dump(),
            levers=payload.levers.model_dump(),
            cascade_config=payload.cascade_config,
        )
        self._db.add(scenario)
        await self._db.flush()
        return scenario

    async def update(self, scenario: Scenario, payload: ScenarioUpdate) -> Scenario:
        _occ = frozenset({"expected_updated_at", "force_override"})
        data = payload.model_dump(exclude_none=True, exclude=_occ)
        if "regulations" in data:
            data["regulations"] = payload.regulations.model_dump()  # type: ignore[union-attr]
        if "levers" in data:
            data["levers"] = payload.levers.model_dump()  # type: ignore[union-attr]
        for field, value in data.items():
            setattr(scenario, field, value)
        scenario.updated_at = datetime.now(timezone.utc)
        await self._db.flush()
        return scenario

    async def archive(self, scenario: Scenario) -> Scenario:
        scenario.archived_at = datetime.now(timezone.utc)
        await self._db.flush()
        return scenario

    async def duplicate(
        self, scenario: Scenario, new_name: str, user_id: uuid.UUID
    ) -> Scenario:
        clone = Scenario(
            id=uuid.uuid4(),
            tenant_id=scenario.tenant_id,
            asset_id=scenario.asset_id,
            created_by=user_id,
            name=new_name,
            description=scenario.description,
            is_baseline=False,
            regulations=scenario.regulations,
            levers=scenario.levers,
            cascade_config=scenario.cascade_config,
        )
        self._db.add(clone)
        await self._db.flush()
        return clone


class CountryDataRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_for_scenario(self, scenario_id: uuid.UUID) -> list[CountryData]:
        result = await self._db.execute(
            select(CountryData).where(CountryData.scenario_id == scenario_id)
        )
        return list(result.scalars().all())

    async def get(
        self, scenario_id: uuid.UUID, country_code: str, tenant_id: uuid.UUID
    ) -> CountryData | None:
        result = await self._db.execute(
            select(CountryData).where(
                CountryData.scenario_id == scenario_id,
                CountryData.country_code == country_code,
                CountryData.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        scenario_id: uuid.UUID,
        tenant_id: uuid.UUID,
        country_code: str,
        payload: CountryDataInput,
    ) -> CountryData:
        _occ = frozenset({"expected_updated_at", "force_override"})
        existing = await self.get(scenario_id, country_code, tenant_id)
        if existing is not None:
            for field, value in payload.model_dump(exclude=_occ).items():
                setattr(existing, field, value)
            existing.updated_at = datetime.now(timezone.utc)
            await self._db.flush()
            return existing

        cd = CountryData(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            scenario_id=scenario_id,
            country_code=country_code,
            **{k: v for k, v in payload.model_dump().items() if k not in _occ},
            updated_at=datetime.now(timezone.utc),
        )
        self._db.add(cd)
        await self._db.flush()
        return cd

    async def delete(self, cd: CountryData) -> None:
        await self._db.delete(cd)
        await self._db.flush()

    async def bulk_create(
        self,
        scenario_id: uuid.UUID,
        tenant_id: uuid.UUID,
        country_map: dict[str, CountryDataInput],
    ) -> list[CountryData]:
        rows = []
        for country_code, payload in country_map.items():
            cd = CountryData(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                scenario_id=scenario_id,
                country_code=country_code,
                **payload.model_dump(),
            )
            self._db.add(cd)
            rows.append(cd)
        await self._db.flush()
        return rows
