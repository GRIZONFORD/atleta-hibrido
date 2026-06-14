"""Adaptador simulado de Yazio.

Yazio no expone una API oficial estable; este mock cubre el bucle nutricional
y permite probar el gating de macros sin dependencias frágiles.
"""
from __future__ import annotations

import random
from datetime import date

from domain.gateways import NutritionGateway
from domain.models import YazioMetrics


class MockYazioAdapter(NutritionGateway):
    """Simula el registro diario de calorías y macronutrientes.

    `scenario`:
        - "deficit":  ingesta proteica baja (debe penalizar recuperación).
        - "superavit": ingesta alta de CHO (apoyo a carga aeróbica).
        - None:        valores realistas de atleta híbrido ~75 kg.
    """

    def __init__(self, scenario: str | None = None, bodyweight_kg: float = 75.0) -> None:
        self._scenario = scenario
        self._bw = bodyweight_kg

    def fetch_daily(self, day: date) -> YazioMetrics:
        rng = random.Random(day.toordinal() + 7)

        if self._scenario == "deficit":
            kcal, prot, carbs, fat = 2250, 95.0, 240.0, 70.0
        elif self._scenario == "superavit":
            kcal, prot, carbs, fat = 3600, 165.0, 520.0, 95.0
        else:
            prot = round(self._bw * rng.uniform(1.7, 2.1), 1)
            carbs = round(self._bw * rng.uniform(4.5, 6.5), 1)
            fat = round(self._bw * rng.uniform(0.8, 1.1), 1)
            kcal = int(prot * 4 + carbs * 4 + fat * 9)

        return YazioMetrics(
            day=day,
            kcal_ingested=kcal,
            protein_g=prot,
            carbs_g=carbs,
            fat_g=fat,
            bodyweight_kg=self._bw,
        )
