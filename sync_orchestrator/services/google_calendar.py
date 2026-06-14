"""GoogleCalendarService - automatizacion sobre Google Calendar API v3.

Mejora v2: la deteccion de conflictos usa `service.freebusy().query()` en lugar
de paginar events().list(). FreeBusy es el endpoint canonico para disponibilidad:
devuelve directamente los rangos ocupados (incluso de varios calendarios), es mas
barato y no expone detalles privados de los eventos.

Flujo de agenda
---------------
    cerebro -> slot preferido (p.ej. 18:00, anti-interferencia mTOR)
        -> freebusy().query() del dia -> intervalos ocupados
        -> SlotFinder.find() -> primer hueco libre de 60-90 min en la ventana
        -> events().insert | events().update (idempotente por extendedProperties)
"""
from __future__ import annotations

import datetime as dt
import os
from typing import Any
from zoneinfo import ZoneInfo

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from domain.models import TrainingDecision
from services.slot_finder import (
    AllowedWindow,
    Interval,
    ScheduleConflictError,
    SlotFinder,
)

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",  # requerido por freebusy
]
APP_TAG = "hybrid-athlete"


class CalendarAuthError(RuntimeError):
    """Fallo de autenticacion que requiere intervencion humana."""


class GoogleCalendarService:
    """Cliente de alto nivel para agendar el bloque de entrenamiento diario."""

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
        calendar_id: str = "primary",
        timezone: str = "America/Bogota",
        window: AllowedWindow | None = None,
    ) -> None:
        self._credentials_path = credentials_path
        self._token_path = token_path
        self._calendar_id = calendar_id
        self._tz = ZoneInfo(timezone)
        self._slot_finder = SlotFinder(window=window)
        self._service = self._build_service()

    # --------------------------------------------------------- autenticacion
    def _build_service(self) -> Any:
        """Construye el cliente con refresh defensivo de OAuth2."""
        creds: Credentials | None = None
        if os.path.exists(self._token_path):
            creds = Credentials.from_authorized_user_file(self._token_path, SCOPES)

        if creds and creds.valid:
            return build("calendar", "v3", credentials=creds, cache_discovery=False)

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # refresh silencioso
            except RefreshError as exc:
                # refresh_token revocado/caducado -> nuevo consentimiento.
                if os.path.exists(self._token_path):
                    os.remove(self._token_path)
                creds = self._run_consent_flow()
                if creds is None:
                    raise CalendarAuthError(
                        "Refresh token invalido y no fue posible re-autenticar."
                    ) from exc
        else:
            creds = self._run_consent_flow()

        self._persist(creds)
        return build("calendar", "v3", credentials=creds, cache_discovery=False)

    def _run_consent_flow(self) -> Credentials | None:
        if not os.path.exists(self._credentials_path):
            raise CalendarAuthError(
                f"No se encontro '{self._credentials_path}'. Descargalo de "
                f"Google Cloud Console (OAuth client ID tipo Desktop)."
            )
        flow = InstalledAppFlow.from_client_secrets_file(self._credentials_path, SCOPES)
        return flow.run_local_server(port=0)

    def _persist(self, creds: Credentials) -> None:
        with open(self._token_path, "w", encoding="utf-8") as fh:
            fh.write(creds.to_json())

    # ------------------------------------------------------------- FreeBusy
    def get_busy_intervals(self, day: dt.date) -> list[Interval]:
        """Consulta freebusy().query() y devuelve los rangos ocupados del dia."""
        time_min = dt.datetime.combine(day, dt.time.min, tzinfo=self._tz)
        time_max = dt.datetime.combine(day, dt.time.max, tzinfo=self._tz)
        body = {
            "timeMin": time_min.isoformat(),
            "timeMax": time_max.isoformat(),
            "timeZone": str(self._tz),
            "items": [{"id": self._calendar_id}],
        }
        try:
            resp = self._service.freebusy().query(body=body).execute()
        except HttpError as exc:
            raise CalendarAuthError(f"Error en freebusy().query(): {exc}") from exc

        cal = resp.get("calendars", {}).get(self._calendar_id, {})
        if cal.get("errors"):
            raise CalendarAuthError(f"FreeBusy devolvio errores: {cal['errors']}")

        intervals: list[Interval] = []
        for slot in cal.get("busy", []):
            intervals.append(
                (
                    dt.datetime.fromisoformat(slot["start"]),
                    dt.datetime.fromisoformat(slot["end"]),
                )
            )
        return intervals

    # ----------------------------------------------------------------- API
    def find_training_block(self, day: dt.date) -> dict[str, Any] | None:
        """Devuelve el bloque previo de la app (idempotencia), o None."""
        start = dt.datetime.combine(day, dt.time.min, tzinfo=self._tz)
        end = dt.datetime.combine(day, dt.time.max, tzinfo=self._tz)
        try:
            resp = self._service.events().list(
                calendarId=self._calendar_id,
                timeMin=start.isoformat(),
                timeMax=end.isoformat(),
                singleEvents=True,
                privateExtendedProperty=f"app={APP_TAG}",
            ).execute()
        except HttpError as exc:
            raise CalendarAuthError(f"Error consultando el calendario: {exc}") from exc
        items = resp.get("items", [])
        return items[0] if items else None

    def resolve_slot(self, day: dt.date, decision: TrainingDecision) -> dt.datetime:
        """Combina FreeBusy + heuristica para devolver el inicio definitivo.

        Excluye el propio bloque de la app de los intervalos ocupados, de modo
        que reprogramar no se 'auto-bloquee'.
        """
        busy = self.get_busy_intervals(day)
        existing = self.find_training_block(day)
        if existing:
            own = self._event_interval(existing)
            if own:
                busy = [b for b in busy if not self._same_interval(b, own)]
        return self._slot_finder.find(
            day=day,
            preferred_hour=decision.start_hour,
            duration_min=decision.duration_min,
            busy=busy,
            tz=self._tz,
        )

    def upsert_training_block(
        self, day: dt.date, decision: TrainingDecision
    ) -> dict[str, Any]:
        """Inserta o reprograma el bloque optimo evitando solapes (FreeBusy)."""
        start_dt = self.resolve_slot(day, decision)
        end_dt = start_dt + dt.timedelta(minutes=decision.duration_min)
        body = self._build_body(decision, start_dt, end_dt)
        existing = self.find_training_block(day)
        try:
            if existing:
                return self._service.events().update(
                    calendarId=self._calendar_id, eventId=existing["id"], body=body
                ).execute()
            return self._service.events().insert(
                calendarId=self._calendar_id, body=body
            ).execute()
        except HttpError as exc:
            raise CalendarAuthError(f"Error al agendar el evento: {exc}") from exc

    # ----------------------------------------------------------- utilidades
    def _event_interval(self, ev: dict[str, Any]) -> Interval | None:
        s = ev.get("start", {}).get("dateTime")
        e = ev.get("end", {}).get("dateTime")
        if s and e:
            return dt.datetime.fromisoformat(s), dt.datetime.fromisoformat(e)
        return None

    @staticmethod
    def _same_interval(a: Interval, b: Interval) -> bool:
        same_start = abs((a[0] - b[0]).total_seconds()) < 60
        same_end = abs((a[1] - b[1]).total_seconds()) < 60
        return same_start and same_end

    def _build_body(
        self, decision: TrainingDecision, start_dt: dt.datetime, end_dt: dt.datetime
    ) -> dict[str, Any]:
        desc_lines = [
            f"Zona: {decision.zone.value}",
            f"Fenotipo: {decision.phenotype.value}",
            f"Objetivo macros: {decision.protein_g_per_kg_target:.1f} g/kg proteina, "
            f"{decision.carbs_g_per_kg_target:.1f} g/kg CHO",
            "",
            f"Justificacion: {decision.rationale}",
        ]
        return {
            "summary": f"[Entreno] {decision.title}",
            "description": "\n".join(desc_lines),
            "start": {"dateTime": start_dt.isoformat(), "timeZone": str(self._tz)},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": str(self._tz)},
            "colorId": "11" if decision.zone.value == "ZONA_DE_LESION" else "10",
            "extendedProperties": {"private": {"app": APP_TAG}},
        }
