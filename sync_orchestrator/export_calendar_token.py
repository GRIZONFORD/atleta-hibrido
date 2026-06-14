"""Exporta token.json de Google Calendar a base64 para Streamlit Secrets.

token.json es JSON (con comillas) → rompería el TOML de Streamlit. Lo codificamos
a base64 (TOML-safe) igual que el token de Garmin.

Ejecutar localmente tras setup_calendar.py:

    sync_orchestrator\\.venv\\Scripts\\python sync_orchestrator\\export_calendar_token.py

Escribe google_secret.toml (gitignored). Copia su línea y AÑÁDELA a tus Streamlit
Secrets, junto a GARMIN_EMAIL / GARMIN_TOKEN_B64. Luego borra el archivo.
"""
from __future__ import annotations

import base64
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    token_path = REPO_ROOT / "token.json"
    if not token_path.exists():
        print(f"⛔ No hay {token_path}")
        print("   Corre primero: python sync_orchestrator/setup_calendar.py")
        return

    raw = token_path.read_text(encoding="utf-8")
    b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")

    out = REPO_ROOT / "google_secret.toml"
    out.write_text(f'GOOGLE_TOKEN_B64 = "{b64}"\n', encoding="utf-8")

    print("\n" + "=" * 64)
    print("  ✅ Secret de Google escrito en:")
    print(f"     {out}")
    print("=" * 64)
    print("  1) Abre ese archivo y copia la línea GOOGLE_TOKEN_B64.")
    print("  2) AÑÁDELA a Streamlit Cloud → Settings → Secrets")
    print("     (debajo de GARMIN_EMAIL / GARMIN_TOKEN_B64) → Save.")
    print("  3) Borra el archivo cuando termines.")
    print("=" * 64 + "\n")


if __name__ == "__main__":
    main()
