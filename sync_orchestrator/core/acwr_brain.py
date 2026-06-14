"""Cerebro algorítmico: correlación ACWR + HRV -> decisión de entrenamiento.

Modelo de carga: Acute:Chronic Workload Ratio (Gabbett, 2016).
    - Sweet spot (optimización):  0.8 <= ACWR <= 1.3
    - Zona de riesgo lesivo:      ACWR > 1.5  (o HRV muy deprimida)
    - Subcarga funcional:         ACWR < 0.8

La HRV se evalúa SIEMPRE relativa a la línea base individual (hrv_ratio),
no contra umbrales poblacionales absolutos.
"""
from __future__ import annotations

from domain.models import (
    AthleteDailySnapshot,
    FatigueZone,
    Phenotype,
    Slot,
    TrainingDecision,
)


class AcwrBrain:
    """Servicio de dominio sin estado: entrada DTO -> salida decisión."""

    # Umbrales parametrizables (Open/Closed: se ajustan sin tocar la lógica).
    ACWR_HIGH_RISK: float = 1.5
    ACWR_UPPER_SWEET: float = 1.3
    ACWR_LOWER_SWEET: float = 0.8
    HRV_SUPPRESSED: float = 0.93   # <93% de la baseline => SNA estresado

    def evaluate(
        self,
        snapshot: AthleteDailySnapshot,
        phenotype: Phenotype = Phenotype.HYPERTROPHY,
    ) -> TrainingDecision:
        zone = self._classify_zone(snapshot)
        return self._prescribe(zone, snapshot, phenotype)

    # ---------------------------------------------------------------- interno
    def _classify_zone(self, s: AthleteDailySnapshot) -> FatigueZone:
        acwr, hrv = s.acwr, s.hrv_ratio

        if acwr > self.ACWR_HIGH_RISK or hrv < self.HRV_SUPPRESSED:
            return FatigueZone.LESION
        if acwr < self.ACWR_LOWER_SWEET:
            return FatigueZone.FUNCIONAL_BAJO
        return FatigueZone.OPTIMIZACION

    def _prescribe(
        self,
        zone: FatigueZone,
        s: AthleteDailySnapshot,
        phenotype: Phenotype,
    ) -> TrainingDecision:
        # Macros base; se ajustan por carga aeróbica (CHO) y fatiga (proteína).
        carbs_target = 7.0 if s.acwr > 1.2 else 5.5
        protein_target = 2.0 if phenotype in (Phenotype.MAX_POWER, Phenotype.HYPERTROPHY) else 1.8

        if zone is FatigueZone.LESION:
            return TrainingDecision(
                zone=zone,
                title="Rodaje de Recuperación Z2",
                slot=Slot.AM,
                start_hour=8,
                duration_min=40,
                phenotype=Phenotype.BASE,
                protein_g_per_kg_target=protein_target + 0.2,  # apoyo reparación
                carbs_g_per_kg_target=carbs_target,
                rationale=(
                    f"ACWR={s.acwr:.2f} o HRV={s.hrv_ratio:.2f}x baseline en zona de "
                    f"riesgo. Sin alto impacto (pliometría off). Regeneración aeróbica."
                ),
            )

        if zone is FatigueZone.FUNCIONAL_BAJO:
            return TrainingDecision(
                zone=zone,
                title="Bloque de Construcción: Fuerza + Volumen Z2",
                slot=Slot.PM,
                start_hour=18,
                duration_min=75,
                phenotype=phenotype,
                protein_g_per_kg_target=protein_target,
                carbs_g_per_kg_target=carbs_target,
                rationale=(
                    f"ACWR={s.acwr:.2f} (<0.8): margen para construir. Carga acentuada "
                    f"con separación AM/PM para preservar mTOR."
                ),
            )

        # OPTIMIZACION
        if phenotype in (Phenotype.MAX_POWER, Phenotype.HYPERTROPHY):
            title = "Fuerza Hipertrofia Tren Inferior + Contrast"
        else:
            title = "Pliometría Reactiva + Ritmo Específico"
        return TrainingDecision(
            zone=zone,
            title=title,
            slot=Slot.PM,
            start_hour=18,
            duration_min=80,
            phenotype=phenotype,
            protein_g_per_kg_target=protein_target,
            carbs_g_per_kg_target=carbs_target,
            rationale=(
                f"ACWR={s.acwr:.2f} en sweet spot y HRV={s.hrv_ratio:.2f}x baseline. "
                f"Ventana adaptativa: estímulo de calidad acentuado."
            ),
        )
