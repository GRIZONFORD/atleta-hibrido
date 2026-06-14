"""Adaptador real de Garmin Connect.

Autenticación: corre `python setup_garmin.py` una sola vez desde el terminal.
El token queda en .garth_token/ y el dashboard lo reutiliza sin contraseña.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from domain.models import GarminMetrics

GARTH_HOME = Path(__file__).resolve().parent.parent / ".garth_token"


class RealGarminAdapter:
    """Consulta Garmin Connect en vivo usando el token guardado."""

    def __init__(self) -> None:
        import json
        import os
        from garminconnect import Garmin

        token_b64 = os.environ.get("GARMIN_TOKEN_B64")
        if token_b64:
            # ☁️ Nube: token inyectado como variable de entorno (Streamlit secret).
            # El secret es base64 del JSON de sesión (codificado así para ser
            # TOML-safe). Lo decodificamos al JSON original; garminconnect detecta
            # strings >512 chars como datos de token directos (no como ruta).
            import base64

            email = os.environ.get("GARMIN_EMAIL", "")
            token_json = base64.b64decode(token_b64).decode("utf-8")
            self._api = Garmin(email=email, password="placeholder")
            self._api.login(tokenstore=token_json)
        else:
            # 💻 Local: token persistido en .garth_token por setup_garmin.py
            config_file = GARTH_HOME / "config.json"
            email = json.loads(config_file.read_text(encoding="utf-8")).get("email", "")
            self._api = Garmin(email=email, password="placeholder")
            self._api.login(tokenstore=str(GARTH_HOME))

    # ------------------------------------------------------------------
    def fetch_daily(self, day: date) -> GarminMetrics:
        date_str = day.isoformat()

        hrv_rmssd, hrv_baseline = 55.0, 55.0
        try:
            hrv_data = self._api.get_hrv_data(date_str)
            summary = hrv_data.get("hrvSummary", {})
            hrv_rmssd = float(summary.get("lastNight") or 55)
            baseline = summary.get("baseline") or {}
            hrv_baseline = float(baseline.get("balancedLow") or hrv_rmssd)
        except Exception:
            pass

        resting_hr = 50
        try:
            stats = self._api.get_stats(date_str)
            resting_hr = int(stats.get("restingHeartRate") or 50)
        except Exception:
            pass

        start_7 = (day - timedelta(days=6)).isoformat()
        start_28 = (day - timedelta(days=27)).isoformat()
        mileage_7d = 0.0
        acute_load = 0.0

        try:
            acts_7 = self._api.get_activities_by_date(start_7, date_str, "running")
            for a in acts_7:
                mileage_7d += (a.get("distance") or 0) / 1000
                # Training load: usa el campo nativo si existe, sino: minutos × efecto
                load = (
                    a.get("activityTrainingLoad")
                    or a.get("trainingLoadPeak")
                    or (a.get("duration", 0) / 60 * (a.get("trainingEffect") or 2))
                )
                acute_load += float(load)
        except Exception:
            pass

        chronic_load = acute_load  # fallback: misma carga si no hay datos 28d
        try:
            acts_28 = self._api.get_activities_by_date(start_28, date_str, "running")
            total_28 = 0.0
            for a in acts_28:
                load = (
                    a.get("activityTrainingLoad")
                    or a.get("trainingLoadPeak")
                    or (a.get("duration", 0) / 60 * (a.get("trainingEffect") or 2))
                )
                total_28 += float(load)
            chronic_load = total_28 / 4  # promedio semanal en 4 semanas
        except Exception:
            pass

        return GarminMetrics(
            day=day,
            hrv_rmssd_ms=hrv_rmssd,
            hrv_baseline_ms=max(hrv_baseline, 1.0),
            acute_load=max(acute_load, 1.0),
            chronic_load=max(chronic_load, 1.0),
            resting_hr=resting_hr,
            mileage_7d_km=round(mileage_7d, 1),
        )

    @classmethod
    def is_authenticated(cls) -> bool:
        import os
        return GARTH_HOME.exists() or bool(os.environ.get("GARMIN_TOKEN_B64"))
