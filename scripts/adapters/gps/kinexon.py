"""Adaptador de GPS para Kinexon — STUB, fase 2.

Kinexon tiene una API REST propia, pensada justamente para esto (acceso
programático a datos de sesiones/jugadores). A diferencia de Catapult o
STATSports, no hace falta pedir que te habiliten nada especial: es parte
del producto. Referencia: https://kinexon-sports.com/ (portal de API / Kinexon
Sports App).

Para terminar este adaptador hacen falta, del club que la use:
- API key / credenciales de su cuenta Kinexon.
- La doc concreta de los endpoints que les dio Kinexon (varía según el
  paquete contratado — Perform GPS Pro, LPS, etc.), para mapear su
  respuesta a RegistroSesion.

No se armó el detalle de requests todavía porque no hay cuenta real contra
la cual probar — el login/API de Catapult en `catapult.py` sí está
verificado contra una cuenta real (la de Tigre) y sirve de modelo de cómo
estructurar esto (login/token, función de requests autenticados, mapeo de
nombre de jugador -> plantel propio).
"""
import datetime
from typing import List

from .base import RegistroSesion


def fetch_sesiones(config: dict, desde: datetime.date, hasta: datetime.date) -> List[RegistroSesion]:
    raise NotImplementedError(
        "Adaptador de Kinexon sin terminar — hace falta API key real del club "
        "y la doc de sus endpoints para mapear la respuesta."
    )
