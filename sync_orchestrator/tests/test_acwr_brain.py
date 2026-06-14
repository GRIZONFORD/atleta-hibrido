"""Tests del cerebro: clasificación de zona y prescripción (ACWR + HRV)."""
from __future__ import annotations

from datetime import date

import pytest

from core.acwr_brain import AcwrBrain
from domain.models import (
    AthleteDailySnapshot, FatigueZone, GarminMetrics, Phenotype, Slot, YazioMetrics,
)


def _snap(acute, chronic, hrv, baseline=55.0) -> AthleteDailySnapshot:
    g = GarminMetrics(
        day=date(2026, 6, 14), hrv_rmssd_ms=hrv, hrv_baseline_ms=baseline,
        acute_load=acute, chronic_load=chronic, resting_hr=48, mileage_7d_km=60.0,
    )
    y = YazioMetrics(
        day=date(2026, 6, 14), kcal_ingested=2500, protein_g=120.0,
        carbs_g=300.0, fat_g=70.0, bodyweight_kg=60.0,
    )
    return AthleteDailySnapshot(g, y)


brain = AcwrBrain()


def test_acwr_alto_es_lesion():
    # acwr = 980/600 = 1.63 > 1.5 -> LESION
    d = brain.evaluate(_snap(980, 600, hrv=55), Phenotype.HYPERTROPHY)
    assert d.zone is FatigueZone.LESION
    assert d.slot is Slot.AM  # regeneración matutina


def test_hrv_deprimida_es_lesion_aunque_acwr_ok():
    # acwr en sweet spot pero hrv 38/55 = 0.69 < 0.93 -> LESION
    d = brain.evaluate(_snap(600, 600, hrv=38), Phenotype.HYPERTROPHY)
    assert d.zone is FatigueZone.LESION


def test_acwr_bajo_es_funcional_bajo():
    # acwr = 360/620 = 0.58 < 0.8 -> FUNCIONAL_BAJO
    d = brain.evaluate(_snap(360, 620, hrv=62, baseline=56), Phenotype.HYPERTROPHY)
    assert d.zone is FatigueZone.FUNCIONAL_BAJO


def test_sweet_spot_es_optimizacion():
    # acwr = 640/600 = 1.07, hrv 58/55 = 1.05 -> OPTIMIZACION
    d = brain.evaluate(_snap(640, 600, hrv=58), Phenotype.HYPERTROPHY)
    assert d.zone is FatigueZone.OPTIMIZACION
    assert d.slot is Slot.PM  # separación mTOR/AMPK


def test_proteina_hipertrofia_es_2g():
    d = brain.evaluate(_snap(640, 600, hrv=58), Phenotype.HYPERTROPHY)
    assert d.protein_g_per_kg_target == pytest.approx(2.0)


def test_lesion_sube_proteina_para_reparacion():
    d = brain.evaluate(_snap(980, 600, hrv=55), Phenotype.HYPERTROPHY)
    assert d.protein_g_per_kg_target == pytest.approx(2.2)  # 2.0 + 0.2


def test_carbos_suben_con_carga_aerobica_alta():
    # acwr 1.63 > 1.2 -> 7.0 g/kg CHO
    d = brain.evaluate(_snap(980, 600, hrv=55), Phenotype.HYPERTROPHY)
    assert d.carbs_g_per_kg_target == pytest.approx(7.0)


def test_fenotipo_base_baja_proteina():
    d = brain.evaluate(_snap(640, 600, hrv=58), Phenotype.BASE)
    assert d.protein_g_per_kg_target == pytest.approx(1.8)
