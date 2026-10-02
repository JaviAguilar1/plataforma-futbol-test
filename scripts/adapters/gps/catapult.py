"""Adaptador de GPS para Catapult (OpenField) — STUB, fase 2.

Dos caminos posibles, en orden de preferencia:

1. **API oficial ("Catapult Connect" / OpenField Cloud API):** hay que
   pedirle a Catapult Sports (Customer Success del club) que habilite la
   generación de API tokens en la cuenta. Es la vía soportada y documentada
   por Catapult — preferible si el club puede conseguir el token.
   Doc: https://support.catapultsports.com/hc/en-us/articles/360002186896-API-Tokens

2. **API interna de OpenField (reverse-engineered):** Tigre ya tiene esto
   funcionando contra su propia cuenta (login + token + bajar actividades y
   stats por jugador) sin esperar que Catapult habilite nada — ver
   `catapult_login`/`catapult_get`/`catapult_stats_post` en el
   `scripts/scrape_tablas.py` del repo de Tigre como referencia de:
   - El login real NO es en el dominio que muestra el `<form>` del sitio,
     sino en `backend-us.openfield.catapultsports.com` (auth tipo Laravel
     Sanctum: cookie CSRF primero, header `X-XSRF-TOKEN` después).
   - Los endpoints de actividades/stats de esa misma API.
   Ese código tiene hardcodeado el nombre del equipo en Catapult y aliases
   de jugadores de Tigre — NO copiar tal cual, sí copiar el mecanismo de
   login/requests y volver a armar el mapeo de nombres con los datos reales
   del club nuevo.

Para terminar este adaptador hacen falta, como mínimo:
- Credenciales de Catapult del club nuevo (para probar cuál de los dos
  caminos funciona).
- El nombre exacto del/los equipo(s) en Catapult, para poder resolver
  `team_id` -> categoría del club.
"""
import datetime
from typing import List

from .base import RegistroSesion


def fetch_sesiones(config: dict, desde: datetime.date, hasta: datetime.date) -> List[RegistroSesion]:
    raise NotImplementedError(
        "Adaptador de Catapult sin terminar — ver el docstring de este archivo. "
        "Hace falta: credenciales del club + decidir API oficial vs. interna."
    )
