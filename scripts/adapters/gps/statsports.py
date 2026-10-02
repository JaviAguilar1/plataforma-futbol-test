"""Adaptador de GPS para STATSports (Apex) — STUB, fase 2.

A diferencia de Catapult/Kinexon, STATSports no tiene una API pública propia
para cualquier cliente: el dato sale de su software (PRO Series) como
CSV/XML/PDF, o se conecta a través de una plataforma intermedia de gestión
de atletas (AthleteMonitoring, Kitman Labs, etc.) si el club ya paga una de
esas.

Dos caminos:
1. **Si el club ya usa alguna plataforma intermedia con integración
   STATSports ya armada** (AthleteMonitoring, Kitman Labs...): lo más fácil
   es traer el dato desde ESA plataforma (si tiene su propia API) en vez de
   escribir esto.
2. **Si no:** STATSports exporta CSV desde su software — en ese caso NO hace
   falta este adaptador, alcanza con `csv_generico.py` apuntando a la
   carpeta donde el club deja esos export y completando `mapeoColumnas` con
   los encabezados reales de ese CSV (se arma en minutos, sin programar).

Este archivo queda como stub por si en algún momento STATSports habilita una
API directa para el club (preguntarles a ellos primero antes de invertir
tiempo en reversearla).
"""
import datetime
from typing import List

from .base import RegistroSesion


def fetch_sesiones(config: dict, desde: datetime.date, hasta: datetime.date) -> List[RegistroSesion]:
    raise NotImplementedError(
        "STATSports no tiene API pública confirmada. Si el club la usa, "
        "probar primero con csv_generico.py sobre su export CSV/XML."
    )
