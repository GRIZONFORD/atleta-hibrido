"""Autenticación única de Google Calendar (local).

Requiere `credentials.json` (OAuth client tipo *Desktop*) en la RAÍZ del repo.
Abre el navegador para que autorices y guarda `token.json` en la raíz.

Ejecutar UNA vez localmente, desde la raíz del repo:

    sync_orchestrator\\.venv\\Scripts\\python sync_orchestrator\\setup_calendar.py

Si tu app OAuth está en modo "Testing", el refresh token caduca en ~7 días.
Para un token estable, publica la pantalla de consentimiento ("In production").
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from services.google_calendar import SCOPES  # noqa: E402
from google_auth_oauthlib.flow import InstalledAppFlow  # noqa: E402


def main() -> None:
    creds_path = REPO_ROOT / "credentials.json"
    token_path = REPO_ROOT / "token.json"

    if not creds_path.exists():
        print(f"⛔ No se encontró {creds_path}")
        print("   Descárgalo de Google Cloud Console:")
        print("   APIs y servicios → Credenciales → Crear credenciales →")
        print("   ID de cliente de OAuth → Tipo: 'Aplicación de escritorio'.")
        print("   Renómbralo a credentials.json y ponlo en la raíz del repo.")
        return

    print("Abriendo navegador para autorizar Google Calendar...")
    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json(), encoding="utf-8")

    print(f"\n✅ token.json guardado en {token_path}")
    print("Para usarlo en la nube, ahora corre:")
    print("   sync_orchestrator\\.venv\\Scripts\\python sync_orchestrator\\export_calendar_token.py")


if __name__ == "__main__":
    main()
