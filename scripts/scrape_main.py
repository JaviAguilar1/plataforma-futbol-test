#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquesta los adaptadores configurados en club.json:
- Liga: genera data/tablas.json (tabla de posiciones + fixture por
  categoría), un archivo ESTÁTICO que index.html lee directo. Son datos
  públicos de la liga, no hace falta Firebase.
- GPS: sube las sesiones a Firebase (temporadas/<año>/gps/<cat>/<sesión>),
  detrás del muro de ingreso — NO a un archivo del repo, porque son datos
  por jugador. Necesita IMPORTADOR_EMAIL / IMPORTADOR_PASSWORD de una cuenta
  con rol "importador" (solo puede escribir sesiones de GPS).

Correr desde la raíz del repo:  python scripts/scrape_main.py

No rompe nada si una categoría/adaptador falla: la deja afuera del JSON de
salida con un aviso por consola, en vez de cortar toda la corrida (mismo
criterio que usa el scraper de Tigre: mejor datos parciales que nada).
"""
import datetime
import importlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)  # los adaptadores se importan como scripts.adapters.*

from scripts.firebase_rest import leer_config_firebase, login, pedir_json, slug_nombre  # noqa: E402
CONFIG_PATH = os.path.join(RAIZ, "config", "club.json")
CONFIG_EJEMPLO_PATH = os.path.join(RAIZ, "config", "club.example.json")
SALIDA_TABLAS = os.path.join(RAIZ, "data", "tablas.json")


def cargar_config():
    ruta = CONFIG_PATH if os.path.exists(CONFIG_PATH) else CONFIG_EJEMPLO_PATH
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def cargar_adapter(paquete: str, nombre: str):
    if nombre == "manual":
        return None
    return importlib.import_module(f"scripts.adapters.{paquete}.{nombre}")


def correr_liga(config: dict):
    nombre_adapter = config.get("fuentes", {}).get("liga", {}).get("adapter", "manual")
    adapter = cargar_adapter("liga", nombre_adapter)
    if adapter is None:
        print("[liga] adapter = manual, no hay nada que scrapear.")
        return {}, {}

    categorias_out = {}
    fixture_out = {}
    for categoria in config["temporada"]["categorias"]:
        try:
            filas = adapter.fetch_tabla_posiciones(config, categoria)
            categorias_out[categoria["id"]] = filas
            print(f"[liga] {categoria['id']}: {len(filas)} equipos en la tabla")
        except Exception as e:
            print(f"[liga][WARN] tabla de {categoria['id']} falló: {e}", file=sys.stderr)
        try:
            partidos = adapter.fetch_fixture(config, categoria)
            fixture_out[categoria["id"]] = partidos
            print(f"[liga] {categoria['id']}: {len(partidos)} partidos en el fixture")
        except NotImplementedError:
            pass
        except Exception as e:
            print(f"[liga][WARN] fixture de {categoria['id']} falló: {e}", file=sys.stderr)
    return categorias_out, fixture_out


def correr_gps(config: dict):
    nombre_adapter = config.get("fuentes", {}).get("gps", {}).get("adapter", "manual")
    adapter = cargar_adapter("gps", nombre_adapter)
    if adapter is None:
        print("[gps] adapter = manual, no hay nada que importar.")
        return None

    hasta = datetime.date.today()
    desde = hasta - datetime.timedelta(days=14)
    try:
        sesiones = adapter.fetch_sesiones(config, desde, hasta)
        print(f"[gps] {len(sesiones)} registros nuevos ({desde} a {hasta})")
        return [
            {**r, "fecha": r["fecha"].isoformat()} if isinstance(r.get("fecha"), datetime.date) else r
            for r in sesiones
        ]
    except NotImplementedError as e:
        print(f"[gps][INFO] adapter '{nombre_adapter}' todavía no está terminado: {e}")
        return None
    except Exception as e:
        print(f"[gps][WARN] falló: {e}", file=sys.stderr)
        return None


def subir_gps(config: dict, registros: list):
    """Agrupa los registros por (categoría, día, tipo) y sube cada sesión entera.

    Subir de nuevo la misma ventana de días reemplaza esas sesiones con lo
    mismo, así que correrlo seguido no duplica nada.
    """
    email, password = os.environ.get("IMPORTADOR_EMAIL"), os.environ.get("IMPORTADOR_PASSWORD")
    if not email or not password:
        print("[gps][ERROR] faltan IMPORTADOR_EMAIL / IMPORTADOR_PASSWORD (cuenta con rol 'importador'): no se subió nada.", file=sys.stderr)
        return
    api_key, db_url, _ = leer_config_firebase()
    token = login(api_key, email, password)
    temporada = pedir_json(f"{db_url}/temporadasInfo/activa.json?auth={token}") or str(config["temporada"]["anio"])
    nombre_adapter = config["fuentes"]["gps"]["adapter"]

    sesiones = {}
    sin_categoria = 0
    for r in registros:
        if not r.get("categoriaId") or not r.get("jugador"):
            sin_categoria += 1
            continue
        tipo = r.get("tipo") or "entrenamiento"
        clave = (r["categoriaId"], r["fecha"], tipo)
        datos = {k: v for k, v in r.items() if k not in ("categoriaId", "fecha", "tipo")}
        sesiones.setdefault(clave, {})[slug_nombre(r["jugador"])] = datos
    if sin_categoria:
        print(f"[gps][WARN] {sin_categoria} registros sin categoría o sin jugador: revisar el mapeo de equipos del adaptador.", file=sys.stderr)

    ahora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for (cat, fecha, tipo), regs in sorted(sesiones.items()):
        sesion = {"fecha": fecha, "tipo": tipo, "fuente": nombre_adapter, "cargadoEl": ahora, "registros": regs}
        pedir_json(f"{db_url}/temporadas/{temporada}/gps/{cat}/{fecha}_{tipo}.json?auth={token}", sesion, "PUT")
        print(f"[gps] {temporada} {cat} {fecha} {tipo}: {len(regs)} jugadores")


def main():
    config = cargar_config()
    os.makedirs(os.path.join(RAIZ, "data"), exist_ok=True)

    tabla_posiciones, fixture = correr_liga(config)
    if tabla_posiciones or fixture:
        with open(SALIDA_TABLAS, "w", encoding="utf-8") as f:
            json.dump({"categorias": tabla_posiciones, "fixture": fixture}, f, ensure_ascii=False, indent=2)
        print(f"Escribí {SALIDA_TABLAS}")

    sesiones_gps = correr_gps(config)
    if sesiones_gps:
        subir_gps(config, sesiones_gps)


if __name__ == "__main__":
    main()
