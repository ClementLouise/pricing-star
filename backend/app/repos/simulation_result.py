"""SimulationResult repository — every query filters by tenant_id per PRD §03."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.simulation_result import SimulationResult


class SimulationResultRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_for_scenario(
        self,
        scenario_id: uuid.UUID,
        tenant_id: uuid.UUID,
        limit: int = 20,
    ) -> list[SimulationResult]:
        result = await self._db.execute(
            select(SimulationResult)
            .where(
                SimulationResult.scenario_id == scenario_id,
                SimulationResult.tenant_id == tenant_id,
            )
            .order_by(SimulationResult.computed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get(self, sim_id: uuid.UUID, tenant_id: uuid.UUID) -> SimulationResult | None:
        result = await self._db.execute(
            select(SimulationResult).where(
                SimulationResult.id == sim_id,
                SimulationResult.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, record: SimulationResult) -> SimulationResult:
        self._db.add(record)
        await self._db.flush()
        return record
