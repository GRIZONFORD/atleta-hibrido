"""FastAPI — expone el dominio del Atleta Híbrido como API REST.

Adaptador de ENTRADA (arquitectura hexagonal): no contiene lógica de negocio,
solo traduce HTTP ↔ dominio. El cerebro (AcwrBrain), los modelos y los servicios
quedan intactos. Esto desacopla la lógica del frontend: hoy Streamlit, mañana
un frontend Next.js premium consumirá ESTA misma API sin tocar el backend.

Correr (desde sync_orchestrator/):
    .venv\\Scripts\\uvicorn api:app --reload
Docs interactivas (Swagger): http://localhost:8000/docs
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))

from adapters.file_yazio import FileYazioAdapter          # noqa: E402
from adapters.mock_garmin import MockGarminAdapter        # noqa: E402
from adapters.real_garmin import RealGarminAdapter        # noqa: E402
from core.acwr_brain import AcwrBrain                     # noqa: E402
from domain.gateways import MetricsGateway                # noqa: E402
from domain.models import AthleteDailySnapshot, Phenotype  # noqa: E402

KCAL_TARGET = 2500

app = FastAPI(
    title="Atleta Híbrido API",
    version="3.0.0",
    description=(
        "Expone el motor de periodización concurrente (ACWR + HRV) como REST. "
        "Adaptador de entrada de la arquitectura hexagonal — el dominio es puro."
    ),
)

# CORS abierto (uso personal). Para producción, restringir a tu dominio de frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


# ── Modelos de respuesta (Pydantic) ─────────────────────────────────────────
class Readiness(BaseModel):
    date: dt.date
    acwr: float
    hrv_ratio: float
    hrv_rmssd_ms: float
    resting_hr: int
    mileage_7d_km: float
    acute_load: float
    zone: str
    battery_pct: float


class Plan(BaseModel):
    date: dt.date
    zone: str
    title: str
    slot: int
    start_hour: int
    duration_min: int
    phenotype: str
    rationale: str
    protein_g_per_kg_target: float
    carbs_g_per_kg_target: float
    protein_g_target: float
    carbs_g_target: float


class NutritionTargets(BaseModel):
    date: dt.date
    bodyweight_kg: float
    protein_g: float
    carbs_g: float
    kcal: int


class TrendPoint(BaseModel):
    date: dt.date
    acwr: float
    acute_load: float
    estado: str


class ScheduleResult(BaseModel):
    status: str
    title: str
    start: str
    end: str


# ── Helpers ──────────────────────────────────────────────────────────────────
def _metrics_adapter(scenario: str | None) -> MetricsGateway:
    """Garmin real si hay token; si no, mock con el escenario pedido."""
    if RealGarminAdapter.is_authenticated():
        try:
            return RealGarminAdapter()
        except Exception:
            pass
    return MockGarminAdapter(scenario or "optimo")


def _snapshot(day: dt.date, scenario: str | None) -> AthleteDailySnapshot:
    g = _metrics_adapter(scenario).fetch_daily(day)
    y = FileYazioAdapter().fetch_daily(day)
    return AthleteDailySnapshot(g, y)


def _battery_pct(hrv_ratio: float) -> float:
    return round(min(max((hrv_ratio - 0.70) / 0.60 * 100, 0), 100), 1)


def _estado(v: float) -> str:
    if v > 1.5:   return "⚠️ Mucha fatiga acumulada — necesitabas descanso"
    if v > 1.3:   return "🔶 Entrenamiento intenso, cerca del límite"
    if v >= 0.8:  return "✅ Ventana perfecta de entrenamiento"
    if v >= 0.5:  return "💤 Cuerpo fresco — puedes cargar más"
    return "🧊 Muy poco estímulo estos días"


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/health", summary="Estado de la API y conexión Garmin")
def health() -> dict:
    return {"status": "ok", "garmin_authenticated": RealGarminAdapter.is_authenticated()}


@app.get("/readiness/today", response_model=Readiness,
         summary="Preparación de hoy: ACWR, HRV, zona y batería")
def readiness_today(scenario: str | None = Query(None, description="Solo mock: optimo|fatiga|subcarga")):
    day = dt.date.today()
    snap = _snapshot(day, scenario)
    decision = AcwrBrain().evaluate(snap, Phenotype.HYPERTROPHY)
    return Readiness(
        date=day, acwr=round(snap.acwr, 3), hrv_ratio=round(snap.hrv_ratio, 3),
        hrv_rmssd_ms=snap.garmin.hrv_rmssd_ms, resting_hr=snap.garmin.resting_hr,
        mileage_7d_km=snap.garmin.mileage_7d_km, acute_load=round(snap.garmin.acute_load, 1),
        zone=decision.zone.value, battery_pct=_battery_pct(snap.hrv_ratio),
    )


@app.get("/plan/today", response_model=Plan,
         summary="Plan de entrenamiento prescrito para hoy")
def plan_today(
    phenotype: Phenotype = Phenotype.HYPERTROPHY,
    scenario: str | None = Query(None, description="Solo mock: optimo|fatiga|subcarga"),
):
    day = dt.date.today()
    snap = _snapshot(day, scenario)
    d = AcwrBrain().evaluate(snap, phenotype)
    bw = snap.yazio.bodyweight_kg or 60.0
    return Plan(
        date=day, zone=d.zone.value, title=d.title, slot=d.slot.value,
        start_hour=d.start_hour, duration_min=d.duration_min, phenotype=d.phenotype.value,
        rationale=d.rationale,
        protein_g_per_kg_target=d.protein_g_per_kg_target,
        carbs_g_per_kg_target=d.carbs_g_per_kg_target,
        protein_g_target=round(d.protein_g_per_kg_target * bw),
        carbs_g_target=round(d.carbs_g_per_kg_target * bw),
    )


@app.get("/nutrition/targets", response_model=NutritionTargets,
         summary="Objetivos de macros para hoy")
def nutrition_targets(
    phenotype: Phenotype = Phenotype.HYPERTROPHY,
    scenario: str | None = Query(None),
):
    day = dt.date.today()
    snap = _snapshot(day, scenario)
    d = AcwrBrain().evaluate(snap, phenotype)
    bw = snap.yazio.bodyweight_kg or 60.0
    return NutritionTargets(
        date=day, bodyweight_kg=bw,
        protein_g=round(d.protein_g_per_kg_target * bw),
        carbs_g=round(d.carbs_g_per_kg_target * bw), kcal=KCAL_TARGET,
    )


@app.get("/trend", response_model=list[TrendPoint],
         summary="Tendencia del índice de fatiga (ACWR) de los últimos N días")
def trend(
    days: int = Query(14, ge=1, le=60),
    scenario: str | None = Query(None),
):
    adapter = _metrics_adapter(scenario)
    today = dt.date.today()
    points: list[TrendPoint] = []
    for i in range(days - 1, -1, -1):
        dd = today - dt.timedelta(days=i)
        g = adapter.fetch_daily(dd)
        snap = AthleteDailySnapshot(g, FileYazioAdapter().fetch_daily(dd))
        points.append(TrendPoint(
            date=dd, acwr=round(snap.acwr, 3),
            acute_load=round(g.acute_load, 1), estado=_estado(snap.acwr),
        ))
    return points


@app.post("/calendar/schedule", response_model=ScheduleResult,
          summary="Agenda el bloque de hoy en Google Calendar (idempotente)")
def schedule(
    phenotype: Phenotype = Phenotype.HYPERTROPHY,
    start_hour: int | None = Query(None, ge=6, le=21, description="Hora manual opcional"),
    scenario: str | None = Query(None),
):
    from services.google_calendar import GoogleCalendarService
    if not GoogleCalendarService.is_authenticated():
        raise HTTPException(status_code=503, detail="Google Calendar no autenticado.")
    day = dt.date.today()
    snap = _snapshot(day, scenario)
    d = AcwrBrain().evaluate(snap, phenotype)
    if start_hour is not None:
        d = dataclasses.replace(d, start_hour=start_hour)
    try:
        ev = GoogleCalendarService(timezone="America/Bogota").upsert_training_block(day, d)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Error al agendar: {exc}") from exc
    return ScheduleResult(
        status="scheduled", title=d.title,
        start=ev["start"]["dateTime"], end=ev["end"]["dateTime"],
    )
