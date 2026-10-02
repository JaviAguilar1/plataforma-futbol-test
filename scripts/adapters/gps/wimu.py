"""Adaptador de GPS para WIMU PRO (RealTrack Systems, hoy parte de Hudl) —
STUB, fase 2.

Es uno de los GPS más usados en fútbol en español (LaLiga, selección
española, clubes de Argentina/México) así que es un candidato realista si el
club nuevo ya tiene GPS. No encontramos documentación pública de una API
REST abierta (puede existir para cuentas enterprise vía Hudl — preguntar a
RealTrack/Hudl directamente si el club tiene soporte contratado).

Mientras tanto, lo práctico: WIMU exporta datos desde su software (SPRO
para post-sesión, o el Cloud) a CSV/Excel. Igual que con STATSports, el
camino más rápido para arrancar es NO escribir este adaptador todavía y usar
`csv_generico.py` apuntando al export real, completando `mapeoColumnas` con
los encabezados que traiga ESE archivo (varían según qué métricas tenga
habilitadas el club).

Si en algún momento se consigue acceso a una API real de RealTrack/Hudl para
el club, completar esto seguiendo el mismo patrón que `catapult.py`.
"""
import datetime
from typing import List

from .base import RegistroSesion


def fetch_sesiones(config: dict, desde: datetime.date, hasta: datetime.date) -> List[RegistroSesion]:
    raise NotImplementedError(
        "No hay API pública confirmada de WIMU/RealTrack. Probar primero con "
        "csv_generico.py sobre el export de SPRO/Cloud."
    )
