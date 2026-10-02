# Reglas de trabajo

- Responder siempre en español (Argentina), tratando de "vos".
- Explicar los pasos de forma simple.
- Antes de tocar código, mostrar el plan de lo que se va a hacer y pedir
  confirmación antes de aplicarlo.
- Usar la skill `ahorro-tokens` para leer/editar archivos grandes sin releer
  ni reescribir de más.

# Qué es este proyecto

Plantilla genérica de seguimiento de equipos de fútbol (resultados, plantel,
GPS/rendimiento físico, tabla de posiciones) para generar **una instancia
propia por club** — repo + Firebase separados, config propia. No es
multi-club: cada club que la use tiene su propia copia configurada.

Nace como generalización de `SEGUIMIENTO-TIGRE-JUVENILES-2026` (que queda
aparte, sin tocarse) para poder ofrecérsela a otro club en 2027.

# Regla de oro: nada hardcodeado de un club real

- Ningún nombre de club, escudo, color, categoría, jugador, credencial o dato
  real va directo en el código. Todo sale de `config/club.json` (real, fuera
  de git) o de `config/firebase.js` (real, fuera de git) — lo que se commitea
  son solo los `.example`.
- Si en algún momento se prueba con datos de un club real para debuggear, no
  se commitean — se usan en local y listo.

# Estado del proyecto

**2026-10-02 — Arranque (Fase 1, núcleo).** Investigación de proveedores de
GPS (Catapult, STATSports, Kinexon, WIMU/RealTrack, Playermaker — ver
`scripts/adapters/gps/`) y decisión de arquitectura: instancia por club,
adaptadores intercambiables para liga (datos de rivales) y GPS. Se arma el
esqueleto: `config/club.example.json`, `index.html` (login, plantel,
partidos/resultados manuales, tabla de posiciones manual), interfaces de
adaptadores (`scripts/adapters/liga/base.py`, `scripts/adapters/gps/base.py`)
con un importador CSV genérico de GPS ya funcional
(`scripts/adapters/gps/csv_generico.py`) y un adaptador de ejemplo de liga
por scraping HTML (`scripts/adapters/liga/generic_html_table.py`). Los
adaptadores de Catapult/Kinexon/STATSports/WIMU quedan como stub documentado
para la Fase 2 (GPS), cuando se sepa qué usa el club real.

**Pendiente (próximas fases, no empezadas):**
- Fase 2 — GPS: terminar adaptadores reales (al menos Catapult, reusando el
  login/API ya probado en Tigre, genérico) y decidir si hace falta sumar
  Kinexon/STATSports/WIMU según el proveedor del club real.
- Fase 3 — Adaptador de liga real (cuando se sepa qué liga/sitio scrapear).
- Fase 4 — lo que hoy tiene Tigre y todavía no está acá: confiabilidad
  cruzada de fuentes, export PDF, video sync, roles finos, etc. — evaluar
  cuáles aplican a un club genérico y cuáles son específicas de cómo trabaja
  Tigre.
