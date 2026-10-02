"""Adaptador de GPS para Catapult (OpenField).

Login y endpoints verificados en producción contra una cuenta real del club
(no inventados): Catapult usa autenticación tipo Laravel Sanctum para SPA —
hay que pedir la cookie CSRF primero (GET /sanctum/csrf-cookie) y devolverla
como header X-XSRF-TOKEN en cada request que escribe algo; además, la
request tiene que llevar Referer/Origin del sitio de OpenField o el
middleware de Sanctum la rechaza con 401 aunque la cookie esté bien puesta.

No hace falta que Catapult te habilite ningún token especial para que esto
funcione: es la misma API interna que usa el sitio web de OpenField para
mostrarte tus propios datos — alcanza con el email/contraseña de la cuenta
del club. (Existe además una API "oficial" soportada, Catapult Connect, que
Catapult habilita a pedido — si el club la consigue, es preferible, pero
necesitaría un cliente HTTP distinto; no está escrita acá.)

Credenciales: variables de entorno `CATAPULT_EMAIL` / `CATAPULT_PASSWORD` —
NUNCA en club.json. Config esperada en club.json -> fuentes.gps.config:
{
  "equipos": { "<nombre exacto del equipo en Catapult>": "<categoria.id>" },
  "soloPartidos": true,
  "regexPartido": " vs |divisi[oó]n",
  "regexEntrenamiento": "\\bmd\\b"
}

`equipos` es el único dato realmente necesario para arrancar: se saca
mirando la respuesta de GET /api/v6/teams con una sesión logueada (el
nombre tal cual lo tiene cargado el club en Catapult).

Qué NO hace, a propósito, para no asumir de más sobre un club que no
conocemos:
- No cruza el nombre del jugador contra ningún plantel propio — devuelve el
  nombre tal cual lo da Catapult. Tigre necesita ese cruce porque el roster
  que arma Catapult por su cuenta con el tiempo queda desactualizado
  (jugadores que cambiaron de categoría o que ya se fueron del club); si al
  club nuevo le pasa lo mismo, conviene sumar la misma lógica acá después,
  una vez que se vea el problema real.
- No mapea la sesión a un "número de fecha" de ningún fixture: devuelve la
  fecha de calendario real de la actividad (eso sí es genérico). Cruzarla
  contra el fixture del club es un problema de una capa más arriba.
"""
import datetime
import http.cookiejar
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import List

from .base import RegistroSesion

API_BASE = "https://backend-us.openfield.catapultsports.com/api/v6"
LOGIN_URL = "https://backend-us.openfield.catapultsports.com/login"
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (seguimiento-club-generico)",
    "Referer": "https://us.openfield.catapultsports.com/",
    "Origin": "https://us.openfield.catapultsports.com",
}

# Nombres de campo reales de /api/v6/stats, confirmados a mano cruzando los
# numeros contra un informe oficial real de Catapult ("Reporte detallado" de
# un partido) -- no son nombres adivinados.
#
# "rhie" (esfuerzos repetidos de alta intensidad) se dejo afuera a proposito:
# la API de Catapult no lo expone (la doc oficial confirma que los bouts de
# RHIE no se pueden pedir por API) -- pedirlo igual no rompe nada, pero
# devuelve 0 siempre, y ese 0 es enganoso (parece "no tuvo ninguno" cuando en
# realidad nunca se pudo medir).
STATS_PARAMS = [
    "athlete_id", "athlete_name", "activity_id", "activity_name",
    "total_duration", "average_distance_session", "meterage_per_minute",
    "velocity_band6_total_distance", "velocity_band7_total_distance", "velocity_band8_total_distance",
    "gen2_velocity_band8_total_effort_count", "max_vel",
    "gen2_acceleration_band8_total_effort_count", "gen2_acceleration_band1_total_effort_count",
    "gen2_acceleration_band2_total_effort_count",
    "max_effort_acceleration", "max_effort_deceleration",
    "high_speed_distance_per_minute", "total_player_load",
]

REGEX_PARTIDO_DEFAULT = r" vs |divisi[oó]n"
REGEX_ENTRENAMIENTO_DEFAULT = r"\bmd\b"


def _xsrf(cj):
    for c in cj:
        if c.name == "XSRF-TOKEN":
            return urllib.parse.unquote(c.value)
    return None


def _login(email: str, password: str):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.open(urllib.request.Request(
        f"{API_BASE.rsplit('/api', 1)[0]}/sanctum/csrf-cookie", headers=REQUEST_HEADERS), timeout=30)

    xsrf = _xsrf(cj)
    if not xsrf:
        raise RuntimeError("No se pudo obtener la cookie XSRF-TOKEN de Catapult.")

    body = json.dumps({"name": email, "password": password}).encode()
    headers = dict(REQUEST_HEADERS)
    headers.update({"Content-Type": "application/json", "Accept": "application/json", "X-XSRF-TOKEN": xsrf})
    try:
        opener.open(urllib.request.Request(LOGIN_URL, data=body, headers=headers), timeout=30)
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", errors="replace")[:200]
        raise RuntimeError(f"Login de Catapult inválido: {detalle}") from e
    return opener, cj


def _get(opener, url):
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    return json.loads(opener.open(req, timeout=30).read().decode("utf-8", errors="replace"))


def _stats_post(opener, cj, activity_ids):
    body = json.dumps({
        "filters": [{"name": "activity_id", "comparison": "=", "values": activity_ids}],
        "group_by": ["athlete", "activity"],
        "parameters": STATS_PARAMS,
        "sorting": ["athlete_name"],
        "source": "cached_stats",
    }).encode()
    headers = dict(REQUEST_HEADERS)
    headers.update({"Content-Type": "application/json", "Accept": "application/json", "X-XSRF-TOKEN": _xsrf(cj)})
    resp = opener.open(urllib.request.Request(f"{API_BASE}/stats", data=body, headers=headers), timeout=30)
    return json.loads(resp.read().decode("utf-8", errors="replace"))


def _es_partido(nombre_actividad: str, regex_partido: str, regex_entrenamiento: str) -> bool:
    if re.search(regex_entrenamiento, nombre_actividad, re.IGNORECASE):
        return False
    return bool(re.search(regex_partido, nombre_actividad, re.IGNORECASE))


def fetch_sesiones(config: dict, desde: datetime.date, hasta: datetime.date) -> List[RegistroSesion]:
    email = os.environ.get("CATAPULT_EMAIL")
    password = os.environ.get("CATAPULT_PASSWORD")
    if not email or not password:
        raise RuntimeError("Faltan las variables de entorno CATAPULT_EMAIL / CATAPULT_PASSWORD.")

    cfg = config.get("fuentes", {}).get("gps", {}).get("config", {})
    equipos = cfg.get("equipos") or {}
    if not equipos:
        raise RuntimeError(
            "Falta 'equipos' en club.json -> fuentes.gps.config: sin eso no se "
            "sabe qué equipo de Catapult corresponde a cada categoría del club."
        )
    regex_partido = cfg.get("regexPartido", REGEX_PARTIDO_DEFAULT)
    regex_entrenamiento = cfg.get("regexEntrenamiento", REGEX_ENTRENAMIENTO_DEFAULT)
    solo_partidos = cfg.get("soloPartidos", True)

    opener, cj = _login(email, password)
    teams = _get(opener, f"{API_BASE}/teams")
    team_ids = {t["name"]: t["id"] for t in teams if t.get("name") in equipos}

    salida: List[RegistroSesion] = []
    for nombre_equipo, team_id in team_ids.items():
        categoria_id = equipos[nombre_equipo]
        actividades = _get(opener, f"{API_BASE}/activities"
                            f"?page=1&page_size=100&sort=-start_time&deleted=0&team_ids={team_id}")

        fecha_por_activity = {}
        tipo_por_activity = {}
        for a in actividades:
            ts = a.get("start_time")
            if not ts:
                continue
            fecha = datetime.datetime.fromtimestamp(ts).date()
            if not (desde <= fecha <= hasta):
                continue
            es_partido = _es_partido(a.get("name") or "", regex_partido, regex_entrenamiento)
            if solo_partidos and not es_partido:
                continue
            fecha_por_activity[a["id"]] = fecha
            tipo_por_activity[a["id"]] = "partido" if es_partido else "entrenamiento"

        if not fecha_por_activity:
            continue

        filas = _stats_post(opener, cj, list(fecha_por_activity.keys()))
        for fila in filas:
            nombre = fila.get("athlete_name")
            activity_id = fila.get("activity_id")
            if not nombre or activity_id not in fecha_por_activity:
                continue
            minutos = round((fila.get("total_duration") or 0) / 60, 1)
            salida.append(RegistroSesion(
                jugador=nombre,
                fecha=fecha_por_activity[activity_id],
                tipo=tipo_por_activity[activity_id],
                categoriaId=categoria_id,
                minutos=minutos,
                distanciaTotalM=fila.get("average_distance_session") or 0,
                distanciaPorMinM=fila.get("meterage_per_minute") or 0,
                metros1821=fila.get("velocity_band6_total_distance") or 0,
                metros2125=fila.get("velocity_band7_total_distance") or 0,
                metros25Mas=fila.get("velocity_band8_total_distance") or 0,
                distanciaAltaVelocidadPorMin=fila.get("high_speed_distance_per_minute") or 0,
                sprints=fila.get("gen2_velocity_band8_total_effort_count") or 0,
                velMaxKmh=fila.get("max_vel") or 0,
                aceleraciones=fila.get("gen2_acceleration_band8_total_effort_count") or 0,
                aceleracionesBanda2=fila.get("gen2_acceleration_band2_total_effort_count") or 0,
                desaceleraciones=fila.get("gen2_acceleration_band1_total_effort_count") or 0,
                aceleracionMaximaIndividual=fila.get("max_effort_acceleration") or 0,
                desaceleracionMaximaIndividual=fila.get("max_effort_deceleration") or 0,
                playerLoad=fila.get("total_player_load"),
            ))
    return salida
