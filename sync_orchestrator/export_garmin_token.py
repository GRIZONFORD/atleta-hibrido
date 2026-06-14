"""Exporta el token Garmin local a base64 para usarlo en Streamlit Cloud.

El token de Garmin vive en .garth_token/ (local, gitignored). La nube no lo tiene.
Este script lo serializa a un string base64 que pegas en los *Secrets* de
Streamlit Cloud (cifrados, NUNCA en el repo).

Uso (localmente, con el token ya creado por setup_garmin.py):

    cd sync_orchestrator
    .venv\\Scripts\\python export_garmin_token.py

Copia las DOS líneas que imprime y pégalas en:
    Streamlit Cloud → tu app → ⋮ Manage app → Settings → Secrets

⚠️  El token ES tu sesión de Garmin: no lo compartas ni lo subas al repo.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

warnings.simplefilter("ignore")  # silenciar deprecation de garth

GARTH_HOME = Path(__file__).resolve().parent / ".garth_token"


def main() -> None:
    if not GARTH_HOME.exists():
        print("⛔ No hay token local en .garth_token/")
        print("   Corre primero:  python setup_garmin.py")
        return

    from garminconnect import Garmin

    email = json.loads(
        (GARTH_HOME / "config.json").read_text(encoding="utf-8")
    ).get("email", "")

    api = Garmin()
    api.client.load(str(GARTH_HOME))   # carga local (sin red)
    token_b64 = api.client.dumps()     # serializa a base64

    # Escribir a ARCHIVO (no imprimir): la terminal parte el token largo con
    # saltos de línea y eso rompe el TOML al pegarlo. El archivo lo mantiene
    # en una sola línea. Está en .gitignore: nunca llega al repo.
    out = Path(__file__).resolve().parent / "streamlit_secrets.toml"
    out.write_text(
        f'GARMIN_EMAIL = "{email}"\n'
        f'GARMIN_TOKEN_B64 = "{token_b64}"\n',
        encoding="utf-8",
    )

    print("\n" + "=" * 64)
    print("  ✅ Secrets escritos en:")
    print(f"     {out}")
    print("=" * 64)
    print("  1) Abre ese archivo (Notepad / VS Code).")
    print("  2) Selecciona TODO (Ctrl+A) y copia (Ctrl+C).")
    print("  3) Pégalo en: Streamlit Cloud -> Settings -> Secrets -> Save.")
    print("  4) Borra el archivo cuando termines (es tu sesion de Garmin).")
    print("=" * 64 + "\n")


if __name__ == "__main__":
    main()
