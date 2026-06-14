"""Adaptador Yazio con persistencia local en JSON.

Yazio no tiene API pública, así que el usuario ingresa sus macros
desde el sidebar del dashboard. Se guardan en yazio_data.json
(una entrada por día ISO) y sobreviven reinicios del servidor.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from domain.models import YazioMetrics

DATA_FILE = Path(__file__).resolve().parent.parent / "yazio_data.json"


class FileYazioAdapter:
    """Lee datos nutricionales desde el archivo JSON local."""

    def fetch_daily(self, day: date) -> YazioMetrics:
        entry = self._load().get(day.isoformat(), {})
        return YazioMetrics(
            day=day,
            kcal_ingested=int(entry.get("kcal", 0)),
            protein_g=float(entry.get("protein_g", 0.0)),
            carbs_g=float(entry.get("carbs_g", 0.0)),
            fat_g=float(entry.get("fat_g", 0.0)),
            bodyweight_kg=float(entry.get("bodyweight_kg", 60.0)),
        )

    @staticmethod
    def save_today(
        kcal: int,
        protein_g: float,
        carbs_g: float,
        fat_g: float,
        bodyweight_kg: float,
    ) -> None:
        data = FileYazioAdapter._load_static()
        data[date.today().isoformat()] = dict(
            kcal=kcal,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            bodyweight_kg=bodyweight_kg,
        )
        DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load(self) -> dict:
        return self._load_static()

    @staticmethod
    def _load_static() -> dict:
        if DATA_FILE.exists():
            try:
                return json.loads(DATA_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}
