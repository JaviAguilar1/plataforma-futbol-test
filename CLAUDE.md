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

**2026-10-02 — Fase 3: adaptadores de liga (datos de rivales).**
`scripts/adapters/liga/generic_html_table.py` ya tiene las dos funciones
terminadas: `fetch_tabla_posiciones` (ya existía) y ahora también
`fetch_fixture`, con el mismo motor de detección de tabla por encabezado
(refactoreado para poder buscar dos tipos de tabla distintos: posiciones y
fixture). Se sumó un segundo adaptador de referencia,
`generic_json_api.py`, para ligas que arman la tabla con JavaScript desde un
endpoint JSON propio (mapeo de campos 100% configurable por rutas tipo
"a.b.c", igual de espíritu que `csv_generico.py` para GPS). Documentados los
dos en `config/README.md` con ejemplo de config completo.

**Sin probar contra una liga real** (no sabemos todavía qué sitio va a
scrapear el club nuevo) — se probaron los dos contra una página HTML y un
JSON armados a mano (con un partido de otro equipo mezclado adentro, un
resultado sin jugar, y local/visitante invertido), verificando que filtran
bien los partidos que no son del club y manejan los partidos sin jugar.
Probarlos de verdad en cuanto se sepa el sitio real.

**2026-10-02 — Campos completos de plantel y partidos, basados en futdetail.**
Se relevó futdetail (ficha de jugador, carga de partido, convocatoria por
partido, estadísticas) para no dejar afuera ningún campo útil. Sumado a
`index.html`:
- **Ficha de jugador** ("Ver ficha" en cada fila de Plantel): DNI, posición
  secundaria, nacionalidad, pasaporte comunitario, obra social, nro.
  afiliado, foto, video promocional, observaciones, y contacto completo
  (jugador, representante, padre, madre). Se guarda con `.update()`, no pisa
  el resto de la ficha.
- **Lesiones** y **Contratos**: tablas nuevas debajo del plantel (jugador +
  fechas + observaciones; contratos calcula "meses restantes" solo).
- **Partidos**: "Detalle" por fecha (competencia, sistema táctico, planes de
  juego con/sin tenencia, penales, descripción, links — ahora sí hay UI para
  los links, antes `linksPartido` estaba en la config pero no se podía cargar
  nada desde la app) y resultado "No Disputado".
- **Convocatoria por partido** (botón "Convocatoria" en cada fecha): una fila
  por jugador del plantel con titular/suplente, dorsal, minutos, goles,
  amarilla/roja, a quién sustituyó, motivo del cambio (táctico/lesión/
  fatiga/disciplina) y jugador destacado — igual al modelo real de futdetail.
  Guarda todo junto con un botón (no por jugador), para no generar un alud de
  escrituras a Firebase.
- **Bug de fondo corregido de paso**: `renderPlantel`/`renderPartidos`/
  `renderTabla` escuchaban Firebase con `.off()+.on()` sobre la categoría
  actual, pero nunca apagaban el listener de la categoría ANTERIOR al
  cambiar de categoría — si esa categoría vieja recibía un cambio después,
  pisaba la pantalla con datos de la categoría equivocada. Ahora
  `suscribirRefs()` (helper nuevo, reusado en las tres vistas) guarda las
  referencias activas y las apaga todas antes de suscribir las nuevas.
- **Sin estadísticas de temporada por jugador todavía** (convocatorias/PJ/
  goles acumulados) — hoy se ven partido por partido en la Convocatoria; se
  podrían calcular sumando `convocatorias/<cat>/*` cuando haga falta.
- Probado sin Firebase real: las funciones que arman el HTML (con datos
  falsos) y las que guardan (con un `db` simulado que solo registra qué
  path/dato intentarían escribir) — sin errores, escriben donde corresponde.
  Falta probarlo contra una base real con datos de verdad.

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
- Fase 3 (resto) — cuando se sepa la liga/sitio real del club nuevo: probar
  `generic_html_table`/`generic_json_api` contra él, o escribir un adaptador
  a medida si ninguno de los dos aplica (sitio con paginación rara, login
  requerido, etc.).
- Fase 4 — lo que hoy tiene Tigre y todavía no está acá: confiabilidad
  cruzada de fuentes, export PDF, video sync, roles finos, etc. — evaluar
  cuáles aplican a un club genérico y cuáles son específicas de cómo trabaja
  Tigre.
