"""SlotFinder — heurística pura de búsqueda de huecos libres.

Se aísla de la API de Google a propósito: recibe una lista de intervalos
ocupados (los que devuelve freebusy().query()) y calcula el mejor hueco
disponible. Al no tener I/O, es 100% testeable sin credenciales (SRP + DIP).

Heurística de desplazamiento
----------------------------
1. Se respeta la franja PREFERIDA del cerebro (p. ej. 18:00 para fuerza,
   protegiendo la separación mTOR/AMPK frente al aeróbico de la mañana).
2. Si la franja preferida choca con un evento ocupado, se exploran offsets
   crecientes (+30, -30, +60, -60, ...) en pasos de 30 min, SIEMPRE dentro
   de las ventanas permitidas del día (p. ej. 06:00–21:00).
3. La primera franja contigua de la duración requerida que no solape con
   ningún intervalo ocupado es la elegida. Si no hay ninguna, se eleva
   ScheduleConflictError para que la capa superior degrade con elegancia.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

Interval = tuple[dt.datetime, dt.datetime]


class ScheduleConflictError(RuntimeError):
    """No existe ningún hueco libre de la duración pedida en el día."""


@dataclass(frozen=True)
class AllowedWindow:
    """Ventana horaria permitida para entrenar (hora local, 24h)."""

    start_hour: int = 6
    end_hour: int = 21


class SlotFinder:
    """Calcula la franja libre óptima a partir de intervalos ocupados."""

    def __init__(self, window: AllowedWindow | None = None, step_min: int = 30) -> None:
        self._window = window or AllowedWindow()
        self._step = step_min

    def find(
        self,
        day: dt.date,
        preferred_hour: int,
        duration_min: int,
        busy: list[Interval],
        tz: dt.tzinfo,
    ) -> dt.datetime:
        """Devuelve el datetime de inicio del primer hueco libre válido."""
        preferred = dt.datetime.combine(
            day, dt.time(hour=preferred_hour), tzinfo=tz
        )
        for start in self._candidate_starts(preferred, day, tz):
            end = start + dt.timedelta(minutes=duration_min)
            if not self._within_window(start, end, day, tz):
                continue
            if not self._overlaps(start, end, busy):
                return start
        raise ScheduleConflictError(
            f"Sin hueco libre de {duration_min} min el {day} "
            f"dentro de {self._window.start_hour}:00–{self._window.end_hour}:00."
        )

    # ----------------------------------------------------------------- interno
    def _candidate_starts(
        self, preferred: dt.datetime, day: dt.date, tz: dt.tzinfo
    ) -> list[dt.datetime]:
        """Genera horas candidatas: preferida primero, luego ±step crecientes."""
        candidates = [preferred]
        # Recorre el día completo en pasos de `step` por ambos lados.
        max_offsets = (self._window.end_hour - self._window.start_hour) * 60 // self._step
        for k in range(1, max_offsets + 1):
            delta = dt.timedelta(minutes=self._step * k)
            candidates.append(preferred + delta)
            candidates.append(preferred - delta)
        return candidates

    def _within_window(
        self, start: dt.datetime, end: dt.datetime, day: dt.date, tz: dt.tzinfo
    ) -> bool:
        win_start = dt.datetime.combine(
            day, dt.time(hour=self._window.start_hour), tzinfo=tz
        )
        win_end = dt.datetime.combine(
            day, dt.time(hour=self._window.end_hour), tzinfo=tz
        )
        return win_start <= start and end <= win_end

    @staticmethod
    def _overlaps(start: dt.datetime, end: dt.datetime, busy: list[Interval]) -> bool:
        """True si [start, end) solapa con algún intervalo ocupado."""
        return any(b_start < end and start < b_end for b_start, b_end in busy)
