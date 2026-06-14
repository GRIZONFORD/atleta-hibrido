"""SyncOrchestrator — coordina ingesta -> cerebro -> calendario.

Depende SOLO de abstracciones (puertos), no de implementaciones concretas:
los adaptadores (mock o reales) y el servicio de calendario se inyectan.
Esto cumple Dependency Inversion y permite ejecutar el pipeline en modo
'dry-run' (sin calendario) para el dashboard.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from core.acwr_brain import AcwrBrain
from domain.gateways import MetricsGateway, NutritionGateway
from domain.models import (
    AthleteDailySnapshot,
    Phenotype,
    TrainingDecision,
)


@dataclass
class PipelineResult:
    """Salida completa del pipeline para visualización/auditoría."""

    snapshot: AthleteDailySnapshot
    decision: TrainingDecision
    calendar_event: dict[str, Any] | None
    calendar_status: str


class SyncOrchestrator:
    """Orquestador central del ecosistema híbrido."""

    def __init__(
        self,
        metrics_gateway: MetricsGateway,
        nutrition_gateway: NutritionGateway,
        brain: AcwrBrain | None = None,
        calendar_service: Any | None = None,  # GoogleCalendarService (opcional)
    ) -> None:
        self._metrics = metrics_gateway
        self._nutrition = nutrition_gateway
        self._brain = brain or AcwrBrain()
        self._calendar = calendar_service

    def run(
        self, day: date, phenotype: Phenotype = Phenotype.HYPERTROPHY
    ) -> PipelineResult:
        # 1) Ingesta paralela conceptual (mocks -> DTOs).
        snapshot = AthleteDailySnapshot(
            garmin=self._metrics.fetch_daily(day),
            yazio=self._nutrition.fetch_daily(day),
        )
        # 2) Cerebro: correlación ACWR + HRV -> decisión.
        decision = self._brain.evaluate(snapshot, phenotype)

        # 3) Calendario (si está inyectado): upsert idempotente.
        event: dict[str, Any] | None = None
        status = "DRY_RUN (sin servicio de calendario)"
        if self._calendar is not None:
            try:
                existing = self._calendar.find_training_block(day)
                event = self._calendar.upsert_training_block(day, decision)
                status = "REPROGRAMADO" if existing else "CREADO"
            except Exception as exc:  # noqa: BLE001 — degradación elegante
                status = f"ERROR: {exc}"

        return PipelineResult(snapshot, decision, event, status)
