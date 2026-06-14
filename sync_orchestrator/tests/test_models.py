"""Tests del dominio puro: propiedades derivadas de AthleteDailySnapshot."""
from __future__ import annotations

from datetime import date

import pytest

from domain.models import AthleteDailySnapshot, GarminMetrics, YazioMetrics


def _garmin(**kw) -> GarminMetrics:
    base = dict(
        day=date(2026, 6, 14), hrv_rmssd_ms=55.0, hrv_baseline_ms=55.0,
        acute_load=600.0, chronic_load=600.0, resting_hr=48, mileage_7d_km=60.0,
    )
    base.update(kw)
    return GarminMetrics(**base)


def _yazio(**kw) -> YazioMetrics:
    base = dict(
        day=date(2026, 6, 14), kcal_ingested=2500, protein_g=120.0,
        carbs_g=300.0, fat_g=70.0, bodyweight_kg=60.0,
    )
    base.update(kw)
    return YazioMetrics(**base)


def test_acwr_es_aguda_sobre_cronica():
    snap = AthleteDailySnapshot(_garmin(acute_load=640, chronic_load=600), _yazio())
    assert snap.acwr == pytest.approx(640 / 600, rel=1e-6)


def test_hrv_ratio_vs_baseline():
    snap = AthleteDailySnapshot(_garmin(hrv_rmssd_ms=58, hrv_baseline_ms=55), _yazio())
    assert snap.hrv_ratio == pytest.approx(58 / 55, rel=1e-6)


def test_protein_g_per_kg():
    snap = AthleteDailySnapshot(_garmin(), _yazio(protein_g=120, bodyweight_kg=60))
    assert snap.protein_g_per_kg == pytest.approx(2.0)


def test_no_divide_por_cero_en_carga_cronica():
    # chronic_load=0 no debe lanzar ZeroDivisionError (guarda 1e-6)
    snap = AthleteDailySnapshot(_garmin(acute_load=500, chronic_load=0), _yazio())
    assert snap.acwr > 0  # número finito, sin excepción


def test_no_divide_por_cero_en_baseline_hrv():
    snap = AthleteDailySnapshot(_garmin(hrv_rmssd_ms=50, hrv_baseline_ms=0), _yazio())
    assert snap.hrv_ratio > 0
