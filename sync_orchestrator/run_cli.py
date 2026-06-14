"""Runner de línea de comandos — ejecuta el pipeline sin Streamlit.

Uso:
    python run_cli.py --garmin fatiga --yazio normal --phenotype HYPERTROPHY
    python run_cli.py --calendar     # intenta agendar en Google Calendar real
"""
from __future__ import annotations

import argparse
from datetime import date

from adapters.mock_garmin import MockGarminAdapter
from adapters.mock_yazio import MockYazioAdapter
from core.orchestrator import SyncOrchestrator
from domain.models import Phenotype


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline Atleta Híbrido")
    parser.add_argument("--garmin", default="optimo",
                        choices=["optimo", "fatiga", "subcarga", "aleatorio"])
    parser.add_argument("--yazio", default="normal",
                        choices=["normal", "deficit", "superavit"])
    parser.add_argument("--phenotype", default="HYPERTROPHY",
                        choices=[p.value for p in Phenotype])
    parser.add_argument("--calendar", action="store_true",
                        help="Agendar en Google Calendar real")
    args = parser.parse_args()

    garmin = MockGarminAdapter(None if args.garmin == "aleatorio" else args.garmin)
    yazio = MockYazioAdapter(None if args.yazio == "normal" else args.yazio)

    calendar = None
    if args.calendar:
        from services.google_calendar import GoogleCalendarService
        calendar = GoogleCalendarService()

    orch = SyncOrchestrator(garmin, yazio, calendar_service=calendar)
    res = orch.run(date.today(), Phenotype(args.phenotype))

    print(f"\n=== SNAPSHOT ===")
    print(f"ACWR={res.snapshot.acwr:.2f} | HRV ratio={res.snapshot.hrv_ratio:.2f}")
    print(f"\n=== DECISIÓN ===")
    print(f"Zona:   {res.decision.zone.value}")
    print(f"Sesión: {res.decision.title} @ {res.decision.start_hour}:00 "
          f"({res.decision.duration_min} min, slot {res.decision.slot.name})")
    print(f"Macros: {res.decision.protein_g_per_kg_target:.1f} g/kg prot | "
          f"{res.decision.carbs_g_per_kg_target:.1f} g/kg CHO")
    print(f"Motivo: {res.decision.rationale}")
    print(f"\n=== CALENDARIO ===\n{res.calendar_status}")


if __name__ == "__main__":
    main()
