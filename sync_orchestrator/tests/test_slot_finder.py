"""Tests del SlotFinder: respeto del horario preferido y esquive de conflictos."""
from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

import pytest

from services.slot_finder import AllowedWindow, ScheduleConflictError, SlotFinder

TZ = ZoneInfo("America/Bogota")
DAY = dt.date(2026, 6, 14)


def _interval(h1, m1, h2, m2):
    return (
        dt.datetime.combine(DAY, dt.time(h1, m1), tzinfo=TZ),
        dt.datetime.combine(DAY, dt.time(h2, m2), tzinfo=TZ),
    )


def test_hora_preferida_libre_se_respeta():
    finder = SlotFinder(AllowedWindow(6, 21))
    start = finder.find(DAY, preferred_hour=18, duration_min=60, busy=[], tz=TZ)
    assert start.hour == 18 and start.minute == 0


def test_conflicto_desplaza_al_siguiente_hueco():
    # 18:00-19:00 ocupado; pide 18:00 60min -> debe moverse (p.ej. 19:00)
    finder = SlotFinder(AllowedWindow(6, 21))
    busy = [_interval(18, 0, 19, 0)]
    start = finder.find(DAY, preferred_hour=18, duration_min=60, busy=busy, tz=TZ)
    end = start + dt.timedelta(minutes=60)
    # el slot elegido no solapa con el bloque ocupado
    b_start, b_end = busy[0]
    assert not (b_start < end and start < b_end)


def test_dia_saturado_lanza_conflicto():
    # todo 6-21 ocupado -> no hay hueco
    finder = SlotFinder(AllowedWindow(6, 21))
    busy = [_interval(6, 0, 21, 0)]
    with pytest.raises(ScheduleConflictError):
        finder.find(DAY, preferred_hour=18, duration_min=60, busy=busy, tz=TZ)


def test_slot_dentro_de_la_ventana_permitida():
    finder = SlotFinder(AllowedWindow(6, 21))
    start = finder.find(DAY, preferred_hour=20, duration_min=60, busy=[], tz=TZ)
    end = start + dt.timedelta(minutes=60)
    assert start.hour >= 6
    assert end.hour <= 21 or (end.hour == 21 and end.minute == 0)
