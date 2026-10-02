"""Adaptador de GPS genérico: importa cualquier CSV que un proveedor pueda
exportar (Playermaker, WIMU/RealTrack, STATSports sin API, etc.), mapeando
sus columnas a nuestro catálogo estándar vía configuración — sin tocar
código para cada proveedor nuevo.

Es el adaptador por default (`fuentes.gps.adapter = "csv_generico"`) porque
funciona sin pedirle una API a nadie: alcanza con el archivo que cualquier
software de GPS ya sabe exportar.

Config esperada en club.json -> fuentes.gps.config:
{
  "carpeta": "data/gps_entrada",
  "separador": ",",
  "formatoFecha": "%d/%m/%Y",
  "mapeoColumnas": {
    "<encabezado real del CSV>": "<campo de RegistroSesion>",
    ...
  },
  "valorTipoPartido": "Match",
  "valorTipoEntrenamiento": "Training"
}

`mapeoColumnas` es lo único que cambia de proveedor a proveedor: se arma
mirando una sola vez el CSV real que exporta el software del club (abrirlo,
ver los nombres de columna, completar el mapeo acá). No hace falta programar
nada nuevo salvo que el proveedor no exporte CSV (ahí sí hace falta un
adaptador por API, ver catapult.py/kinexon.py como referencia de qué forma
tiene que tener).
"""
import csv
import datetime
import glob
import os
from typing import List

from .base import RegistroSesion

CAMPOS_NUMERICOS = {
    "minutos", "distanciaTotalM", "distanciaPorMinM", "metros1821",
    "metros2125", "metros25Mas", "sprints", "velMaxKmh", "aceleraciones",
    "desaceleraciones", "playerLoad",
}


def _parsear_fecha(valor: str, formato: str) -> datetime.date:
    return datetime.datetime.strptime(valor.strip(), formato).date()


def _num(valor: str):
    if valor is None or valor.strip() == "":
        return 0
    try:
        return float(valor.replace(",", "."))
    except ValueError:
        return 0


def fetch_sesiones(config: dict, desde: datetime.date, hasta: datetime.date) -> List[RegistroSesion]:
    cfg = config.get("fuentes", {}).get("gps", {}).get("config", {})
    carpeta = cfg.get("carpeta", "data/gps_entrada")
    separador = cfg.get("separador", ",")
    formato_fecha = cfg.get("formatoFecha", "%d/%m/%Y")
    mapeo = cfg.get("mapeoColumnas") or {}
    tipo_partido = cfg.get("valorTipoPartido", "Match")

    if not mapeo:
        raise RuntimeError(
            "Falta 'mapeoColumnas' en club.json -> fuentes.gps.config: sin eso "
            "no se sabe qué columna del CSV es cada métrica. Ver el docstring "
            "de este archivo."
        )

    salida: List[RegistroSesion] = []
    for ruta in sorted(glob.glob(os.path.join(carpeta, "*.csv"))):
        with open(ruta, newline="", encoding="utf-8-sig") as f:
            lector = csv.DictReader(f, delimiter=separador)
            for fila in lector:
                registro: RegistroSesion = {}
                for columna_csv, campo in mapeo.items():
                    valor = fila.get(columna_csv)
                    if valor is None:
                        continue
                    if campo == "fecha":
                        registro["fecha"] = _parsear_fecha(valor, formato_fecha)
                    elif campo in CAMPOS_NUMERICOS:
                        registro[campo] = _num(valor)
                    elif campo == "tipo":
                        registro["tipo"] = "partido" if valor.strip() == tipo_partido else "entrenamiento"
                    else:
                        registro[campo] = valor.strip()

                if "fecha" not in registro or "jugador" not in registro:
                    continue
                if not (desde <= registro["fecha"] <= hasta):
                    continue
                salida.append(registro)
    return salida
