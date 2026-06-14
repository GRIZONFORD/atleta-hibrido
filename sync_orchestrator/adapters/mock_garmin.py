"""Adaptador simulado de Garmin Connect.

Genera payloads deterministas-pero-realistas de un atleta híbrido sin tocar
la red, evitando los bloqueos de OAuth2/MFA del backend no oficial de Garmin.
Implementa el puerto MetricsGateway (Liskov: intercambiable por el real).
"""
from __future__ import annotations

import random
from datetime import date

from domain.gateways import MetricsGateway
from domain.models import GarminMetrics


class MockGarminAdapter(MetricsGateway):
    """Simula la entrega diaria de HRV y carga de entrenamiento.

    El parámetro `scenario` permite forzar estados para probar el Cerebro:
        - "optimo":   HRV alta, ACWR en sweet spot.
        - "fatiga":   HRV deprimida, ACWR > 1.5 (debe disparar ZONA_DE_LESION).
        - "subcarga": ACWR bajo (margen para construir).
        - None:       valores pseudoaleatorios realistas (semilla por fecha).
    """

    def __init__(self, scenario: str | None = None) -> None:
        self._scenario = scenario

    def fetch_daily(self, day: date) -> GarminMetrics:
        rng = random.Random(day.toordinal())  # determinismo por fecha

        if self._scenario == "fatiga":
            hrv, base, acute, chronic = 38.0, 55.0, 980.0, 600.0
        elif self._scenario == "subcarga":
            hrv, base, acute, chronic = 62.0, 56.0, 360.0, 620.0
        elif self._scenario == "optimo":
            hrv, base, acute, chronic = 58.0, 55.0, 640.0, 600.0
        else:
            base = 55.0
            hrv = round(base * rng.uniform(0.88, 1.10), 1)
            chronic = round(rng.uniform(560, 660), 1)
            acute = round(chronic * rng.uniform(0.75, 1.45), 1)

        return GarminMetrics(
            day=day,
            hrv_rmssd_ms=hrv,
            hrv_baseline_ms=base,
            acute_load=acute,
            chronic_load=chronic,
            resting_hr=rng.randint(42, 50),
            mileage_7d_km=round(rng.uniform(55, 95), 1),
        )
