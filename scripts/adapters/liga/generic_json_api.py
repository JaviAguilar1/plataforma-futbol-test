"""Adaptador de ejemplo: trae datos de liga desde un endpoint JSON en vez de
una <table> HTML -- cada vez más común (muchos sitios modernos no embeben la
tabla en el HTML, la piden ellos mismos a una API propia y la dibujan con
JavaScript, el mismo problema que ya tiene la Reserva de Tigre con su widget
de Opta, donde no hay ninguna <table> que scrapear).

Para encontrar ese endpoint: abrir la página real de la liga, F12 -> pestaña
"Red"/"Network", filtrar por XHR/Fetch, y mirar qué URL devuelve la tabla o
el fixture en JSON -- normalmente alguna de las requests que dispara la
página al cargar.

Como cada API tiene su propia forma, el mapeo de campos es 100% configurable
-- no hay nada adivinado a ciegas, solo hay que mirar la respuesta real del
endpoint y completar las rutas en club.json. Las rutas son "a.b.c" para
navegar objetos anidados, y "a.0.b" para el primer elemento de una lista
dentro de "a".

Config esperada en club.json -> fuentes.liga.config:
{
  "urls": { "<categoria.id>": "https://api.liga.com/standings?..." },
  "rutaFilasTabla": "data.standings",
  "mapeoTabla": {
    "equipo": "team.name", "pj": "played", "pg": "won", "pe": "drawn",
    "pp": "lost", "gf": "goalsFor", "gc": "goalsAgainst", "pts": "points"
  },

  "urlsFixture": { "<categoria.id>": "https://api.liga.com/fixture?..." },
  "rutaFilasFixture": "data.matches",
  "mapeoFixture": {
    "fecha": "matchday", "local": "homeTeam.name", "visitante": "awayTeam.name",
    "resultadoLocal": "score.fullTime.home", "resultadoVisitante": "score.fullTime.away"
  },
  "nombreEquipoEnLiga": "Nombre EXACTO del club tal cual figura en el JSON"
}

`rutaFilasTabla`/`rutaFilasFixture` apuntan a la LISTA de filas (un equipo o
un partido por elemento); si la respuesta YA es esa lista sin ningún
contenedor alrededor, se puede dejar "" (string vacío).

`mapeoFixture.resultadoLocal`/`resultadoVisitante` son para APIs que separan
los goles en dos campos numéricos (lo más común). Si en cambio la API da un
marcador como un solo texto ("2-1"), usar `"resultado": "ruta.al.texto"` en
su lugar -- se detecta solo cuál de los dos estilos se configuró.
"""
import json
import re
import urllib.request
from typing import List

from .base import FilaTabla, PartidoFixture

HEADERS = {"User-Agent": "Mozilla/5.0 (seguimiento-club-generico)", "Accept": "application/json"}


def _descargar_json(url: str):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _valor_por_ruta(obj, ruta: str):
    if not ruta:
        return obj
    actual = obj
    for parte in ruta.split("."):
        if actual is None:
            return None
        if isinstance(actual, list):
            try:
                actual = actual[int(parte)]
            except (ValueError, IndexError):
                return None
        elif isinstance(actual, dict):
            actual = actual.get(parte)
        else:
            return None
    return actual


def _num(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _normalizar_nombre(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _parsear_marcador(resultado: str):
    partes = re.split(r"[-–:]", resultado or "")
    if len(partes) != 2:
        return None, None
    try:
        return int(partes[0].strip()), int(partes[1].strip())
    except ValueError:
        return None, None


def fetch_tabla_posiciones(config: dict, categoria: dict) -> List[FilaTabla]:
    cfg = config.get("fuentes", {}).get("liga", {}).get("config", {})
    url = (cfg.get("urls") or {}).get(categoria["id"])
    mapeo = cfg.get("mapeoTabla") or {}
    if not url or not mapeo:
        raise RuntimeError(
            "Falta 'urls' y/o 'mapeoTabla' en club.json -> fuentes.liga.config "
            "para el adaptador generic_json_api. Ver el docstring de este archivo."
        )
    datos = _descargar_json(url)
    filas = _valor_por_ruta(datos, cfg.get("rutaFilasTabla", "")) or []

    salida: List[FilaTabla] = []
    for i, fila in enumerate(filas, start=1):
        equipo = _valor_por_ruta(fila, mapeo.get("equipo", ""))
        if not equipo:
            continue
        salida.append(FilaTabla(
            pos=_num(_valor_por_ruta(fila, mapeo.get("pos", "")), i),
            equipo=str(equipo),
            pj=_num(_valor_por_ruta(fila, mapeo.get("pj", ""))),
            pg=_num(_valor_por_ruta(fila, mapeo.get("pg", ""))),
            pe=_num(_valor_por_ruta(fila, mapeo.get("pe", ""))),
            pp=_num(_valor_por_ruta(fila, mapeo.get("pp", ""))),
            gf=_num(_valor_por_ruta(fila, mapeo.get("gf", ""))),
            gc=_num(_valor_por_ruta(fila, mapeo.get("gc", ""))),
            pts=_num(_valor_por_ruta(fila, mapeo.get("pts", ""))),
        ))
    return salida


def fetch_fixture(config: dict, categoria: dict) -> List[PartidoFixture]:
    cfg = config.get("fuentes", {}).get("liga", {}).get("config", {})
    url = (cfg.get("urlsFixture") or {}).get(categoria["id"])
    mapeo = cfg.get("mapeoFixture") or {}
    if not url or not mapeo:
        raise RuntimeError(
            "Falta 'urlsFixture' y/o 'mapeoFixture' en club.json -> fuentes.liga.config."
        )
    nombre_club_norm = _normalizar_nombre(cfg.get("nombreEquipoEnLiga") or config.get("club", {}).get("nombre", ""))
    if not nombre_club_norm:
        raise RuntimeError("Falta 'nombreEquipoEnLiga' en club.json -> fuentes.liga.config.")

    datos = _descargar_json(url)
    filas = _valor_por_ruta(datos, cfg.get("rutaFilasFixture", "")) or []

    salida: List[PartidoFixture] = []
    for i, fila in enumerate(filas, start=1):
        local = _valor_por_ruta(fila, mapeo.get("local", "")) or ""
        visitante = _valor_por_ruta(fila, mapeo.get("visitante", "")) or ""
        es_local = nombre_club_norm in _normalizar_nombre(str(local))
        es_visitante = nombre_club_norm in _normalizar_nombre(str(visitante))
        if not es_local and not es_visitante:
            continue  # partido de otro equipo en la misma lista, no del club

        fecha_num = _num(_valor_por_ruta(fila, mapeo.get("fecha", "")), i)
        if "resultado" in mapeo:
            resultado_txt = _valor_por_ruta(fila, mapeo["resultado"])
            goles_local, goles_visitante = _parsear_marcador(str(resultado_txt) if resultado_txt is not None else "")
        else:
            goles_local = _num(_valor_por_ruta(fila, mapeo.get("resultadoLocal", "")), None)
            goles_visitante = _num(_valor_por_ruta(fila, mapeo.get("resultadoVisitante", "")), None)

        hay_resultado = goles_local is not None and goles_visitante is not None
        if es_local:
            salida.append(PartidoFixture(
                fecha=fecha_num, rival=str(visitante), localia="Local",
                resultado=f"{goles_local}-{goles_visitante}" if hay_resultado else None,
                golesFavor=goles_local, golesContra=goles_visitante,
            ))
        else:
            salida.append(PartidoFixture(
                fecha=fecha_num, rival=str(local), localia="Visitante",
                resultado=f"{goles_visitante}-{goles_local}" if hay_resultado else None,
                golesFavor=goles_visitante, golesContra=goles_local,
            ))
    return salida
