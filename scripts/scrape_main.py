#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquesta los adaptadores configurados en club.json y genera data/tablas.json
(tabla de posiciones + fixture por categoría, lo que el adaptador de liga
pueda traer) y, si el adaptador de GPS ya está terminado, data/gps.json
(sesiones por jugador). data/tablas.json es un archivo ESTÁTICO que
index.html lee directo (fetch), sin pasar por Firebase -- mismo patrón que
ya usa Tigre: no hace falta que el scraper tenga credenciales de Firebase
para esta parte.

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
CONFIG_PATH = os.path.join(RAIZ, "config", "club.json")
CONFIG_EJEMPLO_PATH = os.path.join(RAIZ, "config", "club.example.json")
SALIDA_TABLAS = os.path.join(RAIZ, "data", "tablas.json")
SALIDA_GPS = os.path.join(RAIZ, "data", "gps.json")


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
        with open(SALIDA_GPS, "w", encoding="utf-8") as f:
            json.dump(sesiones_gps, f, ensure_ascii=False, indent=2)
        print(f"Escribí {SALIDA_GPS}")


if __name__ == "__main__":
    main()
