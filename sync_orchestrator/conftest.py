"""Configuración de pytest: hace importable el paquete del orquestador.

Inserta sync_orchestrator/ en sys.path para que los tests puedan hacer
`from domain.models import ...` sin instalar el paquete.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
