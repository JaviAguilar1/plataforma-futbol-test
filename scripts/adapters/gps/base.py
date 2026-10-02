"""Interfaz de un adaptador de GPS / rendimiento físico.

Un adaptador devuelve una lista de "registros de sesión por jugador": un
dict por jugador por sesión (partido o entrenamiento), con las métricas ya
traducidas a este catálogo estándar. Es el mismo catálogo de 16 métricas que
ya probó Tigre contra informes reales de Catapult — un adaptador nuevo solo
necesita llenar las claves que su proveedor realmente mide; el resto queda
en 0/None y la app no las muestra.

Dejar un campo en 0 cuando el proveedor no lo mide (en vez de inventarlo) es
a propósito: la ficha de jugador/comparativas tienen que poder distinguir
"no hay dato" de "dio cero".
"""
from typing import TypedDict, Optional, List
import datetime


class RegistroSesion(TypedDict, total=False):
    jugador: str                    # nombre tal cual lo identifica el proveedor
    fecha: datetime.date
    tipo: str                       # "partido" | "entrenamiento"
    categoriaId: Optional[str]
    minutos: float
    distanciaTotalM: float
    distanciaPorMinM: float
    metros1821: float                # distancia en banda 18-21 km/h
    metros2125: float                # distancia en banda 21-25 km/h
    metros25Mas: float                # distancia a +25 km/h
    distanciaAltaVelocidadPorMin: float
    sprints: int
    velMaxKmh: float
    aceleraciones: int               # conteo de aceleraciones "altas" (banda alta del proveedor)
    aceleracionesBanda2: int         # conteo de aceleraciones de una banda mas baja, si el proveedor la separa
    desaceleraciones: int
    aceleracionMaximaIndividual: float    # pico de UN esfuerzo, no un conteo (m/s^2)
    desaceleracionMaximaIndividual: float
    playerLoad: Optional[float]


def fetch_sesiones(config: dict, desde: datetime.date, hasta: datetime.date) -> List[RegistroSesion]:
    raise NotImplementedError
