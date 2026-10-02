"""Interfaz que debe cumplir cualquier adaptador de liga (datos de rivales).

Un adaptador de liga es un módulo en esta carpeta con, como mínimo, la
función `fetch_tabla_posiciones`. `fetch_fixture` es opcional (algunas ligas
no publican el fixture partido a partido en un formato scrapeable).

`config` es el dict completo de club.json; `categoria` es uno de los objetos
de `config["temporada"]["categorias"]`. Cada adaptador decide cómo mapear
esa categoría a la URL/sección real de la liga (normalmente con una tabla
`categoria["id"] -> url` adentro del propio adaptador, ver
generic_html_table.py).

Devolver una lista vacía si no hay datos todavía (ej. arranque de temporada),
nunca None. Si la fuente cambió de formato y el parser no puede leerla más,
levantar una excepción — mejor que `scrape_main.py` no actualice el archivo
de salida a que lo pise con datos vacíos/rotos.
"""
from typing import TypedDict, Optional, List


class FilaTabla(TypedDict):
    pos: int
    equipo: str
    pj: int
    pg: int
    pe: int
    pp: int
    gf: int
    gc: int
    pts: int


class PartidoFixture(TypedDict):
    fecha: int
    rival: str
    localia: str  # "Local" | "Visitante"
    resultado: Optional[str]
    golesFavor: Optional[int]
    golesContra: Optional[int]


def fetch_tabla_posiciones(config: dict, categoria: dict) -> List[FilaTabla]:
    raise NotImplementedError


def fetch_fixture(config: dict, categoria: dict) -> List[PartidoFixture]:
    raise NotImplementedError
