"""Puertos (abstracciones) del dominio — Dependency Inversion Principle.

El Cerebro y el Orquestador dependen de estas interfaces, NUNCA de
implementaciones concretas. Sustituir un mock por el adaptador real
(garth/python-garminconnect) no requiere tocar la lógica de negocio (OCP).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from .models import GarminMetrics, YazioMetrics


class MetricsGateway(ABC):
    """Puerto de ingesta de métricas de hardware (HRV, carga)."""

    @abstractmethod
    def fetch_daily(self, day: date) -> GarminMetrics:
        """Devuelve las métricas normalizadas del día indicado."""
        raise NotImplementedError


class NutritionGateway(ABC):
    """Puerto de ingesta de métricas nutricionales."""

    @abstractmethod
    def fetch_daily(self, day: date) -> YazioMetrics:
        raise NotImplementedError
