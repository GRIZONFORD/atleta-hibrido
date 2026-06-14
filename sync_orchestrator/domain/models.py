"""Modelos de dominio: DTOs inmutables y enumeraciones del Atleta Híbrido.

Este módulo es el lenguaje ubicuo del sistema. No contiene lógica de I/O ni
dependencias externas: es puro dominio y, por tanto, trivialmente testeable.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class FatigueZone(str, Enum):
    """Zona de estado del atleta derivada del modelo ACWR + HRV."""

    LESION = "ZONA_DE_LESION"               # Riesgo alto: descargar / regenerar
    OPTIMIZACION = "ZONA_DE_OPTIMIZACION"   # Ventana adaptativa: cargar
    FUNCIONAL_BAJO = "ZONA_FUNCIONAL_BAJA"  # Subcarga: margen para construir


class Phenotype(str, Enum):
    """Fenotipo de velocidad que pondera el estímulo del microciclo."""

    SPEED_ECONOMY = "SPEED_ECONOMY"   # Pliometría/CEA -> economía a baja velocidad
    MAX_POWER = "MAX_POWER"           # Fuerza >=80% 1RM -> potencia a alta velocidad
    HYPERTROPHY = "HYPERTROPHY"
    BASE = "BASE"


class Slot(int, Enum):
    """Franja intra-día. La separación protege la señalización mTOR/AMPK."""

    AM = 1
    PM = 2


@dataclass(frozen=True)
class GarminMetrics:
    """Payload normalizado proveniente del wearable (Forerunner 255)."""

    day: date
    hrv_rmssd_ms: float          # HRV nocturna (RMSSD)
    hrv_baseline_ms: float       # Media móvil 7d individual del propio atleta
    acute_load: float            # Carga aguda (ventana 7 días, unidades Garmin)
    chronic_load: float          # Carga crónica (ventana 28 días)
    resting_hr: int
    mileage_7d_km: float


@dataclass(frozen=True)
class YazioMetrics:
    """Payload normalizado del registro nutricional."""

    day: date
    kcal_ingested: int
    protein_g: float
    carbs_g: float
    fat_g: float
    bodyweight_kg: float


@dataclass(frozen=True)
class AthleteDailySnapshot:
    """Vista unificada de un día: hardware + nutrición. DTO de transporte."""

    garmin: GarminMetrics
    yazio: YazioMetrics

    @property
    def acwr(self) -> float:
        """Acute:Chronic Workload Ratio (Gabbett, 2016)."""
        return self.garmin.acute_load / max(self.garmin.chronic_load, 1e-6)

    @property
    def hrv_ratio(self) -> float:
        """Desviación de la HRV respecto a la línea base individual."""
        return self.garmin.hrv_rmssd_ms / max(self.garmin.hrv_baseline_ms, 1e-6)

    @property
    def protein_g_per_kg(self) -> float:
        return self.yazio.protein_g / max(self.yazio.bodyweight_kg, 1e-6)


@dataclass(frozen=True)
class TrainingDecision:
    """Resultado del Cerebro: qué entrenar, cuándo y por qué."""

    zone: FatigueZone
    title: str                 # p.ej. "Rodaje de Recuperación Z2"
    slot: Slot
    start_hour: int            # hora local de inicio (24h)
    duration_min: int
    phenotype: Phenotype
    rationale: str
    protein_g_per_kg_target: float
    carbs_g_per_kg_target: float
