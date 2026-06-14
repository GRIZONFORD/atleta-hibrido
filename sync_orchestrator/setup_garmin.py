"""Script de autenticación único para Garmin Connect.

Ejecutar UNA SOLA VEZ desde el terminal (no desde el dashboard):

    cd sync_orchestrator
    python setup_garmin.py

Guarda el token en .garth_token/ para que el dashboard lo reutilice
sin volver a pedir contraseña. Si tienes MFA (autenticación de dos pasos),
el script te lo pedirá aquí en la terminal.

NOTA: Si ves error 429 (rate limit), espera 15-30 minutos y vuelve a intentarlo.
"""
from pathlib import Path
from garminconnect import Garmin

GARTH_HOME = Path(__file__).resolve().parent / ".garth_token"


def main() -> None:
    print("=== Configuración Garmin Connect ===\n")
    email = input("Email de Garmin Connect: ").strip()
    password = input("Contraseña: ").strip()

    print("\nConectando con Garmin Connect...")
    print("(Si tienes verificación en dos pasos activa, revisa tu teléfono/email)\n")

    try:
        api = Garmin(
            email=email,
            password=password,
            prompt_mfa=lambda: input("Código MFA: ").strip(),
        )
        api.login()
    except Exception as e:
        msg = str(e)
        if "429" in msg:
            print("\n⛔ Garmin bloqueó temporalmente tu IP (demasiados intentos).")
            print("   Espera 15-30 minutos y vuelve a ejecutar este script.")
        else:
            print(f"\n⛔ Error al conectar: {e}")
        return

    # Guardar token en formato que garminconnect 0.3.x puede leer
    import json
    GARTH_HOME.mkdir(parents=True, exist_ok=True)
    api.client.dump(str(GARTH_HOME))  # guarda garmin_tokens.json

    # Guardar email para que el adaptador pueda inicializar la sesión
    (GARTH_HOME / "config.json").write_text(
        json.dumps({"email": email}), encoding="utf-8"
    )

    print(f"\n✅ Token guardado en {GARTH_HOME}")
    print("Ya puedes lanzar el dashboard:")
    print("    streamlit run app/dashboard.py\n")


if __name__ == "__main__":
    main()
