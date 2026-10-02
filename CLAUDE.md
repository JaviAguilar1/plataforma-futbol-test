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

**2026-10-02 — Fase 2 (GPS): adaptador de Catapult terminado.**
`scripts/adapters/gps/catapult.py` ya hace el login real (Sanctum: cookie
CSRF + header X-XSRF-TOKEN + Referer/Origin de la SPA) y trae
equipos/actividades/stats, generalizando el mecanismo que ya anda en
producción en Tigre — sin nada hardcodeado de un club real: equipo→categoría
sale de `club.json` (`fuentes.gps.config.equipos`), credenciales de
`CATAPULT_EMAIL`/`CATAPULT_PASSWORD` (variables de entorno, nunca en
config). A diferencia de Tigre, no mapea a "fecha nro" de ningún fixture
(usa la fecha de calendario real de la sesión, más genérico) y no cruza
nombres contra un plantel propio (lo devuelve tal cual lo da Catapult —
sumar ese cruce si en el club real hace falta). `scripts/adapters/gps/base.py`
se amplió con los campos que esto destapó que faltaban (aceleración/
desaceleración por banda y pico individual, distancia a alta velocidad por
minuto).
**Sin probar contra una cuenta real** (no hay credenciales de ningún club
nuevo todavía) — verificado por lectura/comparación fiel contra el mecanismo
de Tigre, compila e importa bien, y los dos chequeos de config faltante
(credenciales, mapeo de equipos) tiran un error claro en vez de romper.
Probar de verdad en cuanto haya una cuenta de Catapult real.

Kinexon/STATSports/WIMU siguen como stub (sin documentación pública de API
confiable para ninguno de los tres) — si el club nuevo usa alguno, arrancar
con `csv_generico` apuntando a su export.

**Pendiente (próximas fases, no empezadas):**
- Fase 2 (resto) — si el club real termina usando Kinexon/STATSports/WIMU
  con API propia, completar ese adaptador con su documentación real.
- Fase 3 — Adaptador de liga real (cuando se sepa qué liga/sitio scrapear).
- Fase 4 — lo que hoy tiene Tigre y todavía no está acá: confiabilidad
  cruzada de fuentes, export PDF, video sync, roles finos, etc. — evaluar
  cuáles aplican a un club genérico y cuáles son específicas de cómo trabaja
  Tigre.
