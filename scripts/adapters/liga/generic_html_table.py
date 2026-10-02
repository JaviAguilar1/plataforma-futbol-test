"""Adaptador de ejemplo: trae la tabla de posiciones de una página que la
publica como una <table> HTML común (sin JavaScript de por medio).

Es el mismo patrón que ya probó la app de Tigre contra ligaprofesional.ar
(ver scrape_tablas.py en el repo de Tigre): bajar el HTML con urllib (sin
dependencias externas) y buscar la tabla cuyo encabezado matchea las
columnas típicas de una tabla de posiciones.

OJO: esto es un PUNTO DE PARTIDA, no algo que vaya a andar solo contra la
liga real del club nuevo. Cada sitio arma su HTML distinto (o ni siquiera
tiene <table>, como le pasa a la Reserva de Tigre con el widget de Opta) —
hay que mirar el sitio real y, si hace falta, escribir un adaptador propio
que cumpla la misma interfaz (base.py).

Config esperada en club.json -> fuentes.liga.config:
{
  "urls": { "<categoria.id>": "https://...": }
}
"""
import re
import urllib.request
from html.parser import HTMLParser
from typing import List

from .base import FilaTabla

HEADERS = {"User-Agent": "Mozilla/5.0 (seguimiento-club-generico)"}

COLUMNAS_ESPERADAS = {
    "equipo": ["equipo", "club", "team"],
    "pj": ["pj", "jugados"],
    "pg": ["pg", "ganados"],
    "pe": ["pe", "empatados"],
    "pp": ["pp", "perdidos"],
    "gf": ["gf", "favor"],
    "gc": ["gc", "contra"],
    "pts": ["pts", "puntos"],
}


class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tablas = []
        self._fila = None
        self._celda = None
        self._en_tabla = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._en_tabla = True
            self.tablas.append([])
        elif tag == "tr" and self._en_tabla:
            self._fila = []
        elif tag in ("td", "th") and self._en_tabla:
            self._celda = []

    def handle_endtag(self, tag):
        if tag == "table":
            self._en_tabla = False
        elif tag == "tr" and self._fila is not None:
            self.tablas[-1].append(self._fila)
            self._fila = None
        elif tag in ("td", "th") and self._celda is not None:
            texto = " ".join("".join(self._celda).split())
            self._fila.append(texto)
            self._celda = None

    def handle_data(self, data):
        if self._celda is not None:
            self._celda.append(data)


def _descargar(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _mapear_columnas(encabezado: List[str]):
    encabezado_norm = [re.sub(r"[^a-z]", "", h.lower()) for h in encabezado]
    indices = {}
    for clave, alias in COLUMNAS_ESPERADAS.items():
        for i, h in enumerate(encabezado_norm):
            if any(a.replace(" ", "") in h for a in alias):
                indices[clave] = i
                break
    return indices


def _elegir_tabla(tablas):
    mejor = None
    mejor_score = 0
    for filas in tablas:
        if not filas:
            continue
        indices = _mapear_columnas(filas[0])
        score = len(indices)
        if score > mejor_score:
            mejor_score = score
            mejor = (filas, indices)
    if mejor is None or mejor_score < 4:
        raise RuntimeError(
            "No se encontró ninguna tabla con pinta de tabla de posiciones "
            "(se esperaban al menos 4 columnas reconocibles: equipo, pj, pts, etc.)"
        )
    return mejor


def _num(v, default=0):
    try:
        return int(re.sub(r"[^\d-]", "", v or "") or default)
    except ValueError:
        return default


def fetch_tabla_posiciones(config: dict, categoria: dict) -> List[FilaTabla]:
    cfg_liga = (config.get("fuentes", {}).get("liga", {}).get("config", {}))
    url = (cfg_liga.get("urls") or {}).get(categoria["id"])
    if not url:
        raise RuntimeError(
            f"Falta la URL de la liga para la categoría {categoria['id']} "
            "en club.json -> fuentes.liga.config.urls"
        )
    html = _descargar(url)
    parser = _TableParser()
    parser.feed(html)
    filas, indices = _elegir_tabla(parser.tablas)

    salida: List[FilaTabla] = []
    for i, fila in enumerate(filas[1:], start=1):
        if "equipo" not in indices or indices["equipo"] >= len(fila):
            continue
        equipo = fila[indices["equipo"]]
        if not equipo:
            continue
        salida.append(FilaTabla(
            pos=i,
            equipo=equipo,
            pj=_num(fila[indices["pj"]]) if "pj" in indices else 0,
            pg=_num(fila[indices["pg"]]) if "pg" in indices else 0,
            pe=_num(fila[indices["pe"]]) if "pe" in indices else 0,
            pp=_num(fila[indices["pp"]]) if "pp" in indices else 0,
            gf=_num(fila[indices["gf"]]) if "gf" in indices else 0,
            gc=_num(fila[indices["gc"]]) if "gc" in indices else 0,
            pts=_num(fila[indices["pts"]]) if "pts" in indices else 0,
        ))
    return salida


def fetch_fixture(config: dict, categoria: dict):
    raise NotImplementedError(
        "Este adaptador de ejemplo no trae fixture, solo tabla de posiciones. "
        "Sumar la lógica si la liga real lo publica en una tabla parecida."
    )
