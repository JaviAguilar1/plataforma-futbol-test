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

**2026-10-22 — Privacidad y cuentas (traído de Tigre, generalizado).**
- **Muro de ingreso**: sin cuenta aprobada no se ve nada (antes la lectura
  era pública: DNI, contactos de padres y datos médicos de menores a la
  vista de cualquiera con el link).
- **Alta de cuentas**: "Crear cuenta" → elige su función → queda pendiente
  (`users/<uid>/rolSolicitado`). Pestaña **Usuarios** (solo admin) con
  contador de pendientes: aprobar (pudiendo cambiar el rol), rechazar,
  cambiar rol, quitar acceso. La pantalla de la persona escucha su propia
  cuenta y se habilita/deshabilita sola. "Olvidé mi contraseña" con el mail
  de Firebase. Errores de login traducidos.
- **Roles que solo ven su categoría**: campo `ve` en `club.json` (default
  todas). Las vistas de todo el club (Inicio, Fixture, Reportes, historial)
  leen categoría por categoría (`paresPorCategoria`), solo las visibles.
- **Reglas con permisos por categoría reales**, no solo en pantalla: el
  admin sincroniza `rolesConfig` desde `club.json` al entrar y las reglas
  controlan `ve`/`edita` por `$cat`. El admin es el rol con id `admin`
  (convención obligatoria: las reglas no pueden leer `club.json`). Reglas
  generadas por `scripts/generar_reglas.py`.
- **Agujero cerrado**: la regla vieja de `users/$uid` dejaba que cualquiera
  que se creara una cuenta (el registro por email está abierto) se
  escribiera `role: "admin"` a sí mismo. Además un rol "lector" podía
  escribir por la API (las reglas solo pedían tener algún rol). Ahora solo
  el admin escribe `role`, y escribir exige poder editar esa categoría.
- Distinto de Tigre: allá los roles están escritos a mano dentro de las
  reglas y la limitación por categoría es solo en pantalla.

Probado contra Firebase real: sin sesión no se lee nada; admin entra y
todas las vistas andan; cuenta nueva desde la UI → pendiente, sin poder
leer nada ni asignarse admin (ni con `set` ni con `update`); el admin la ve
en "Usuarios (1 pendiente)" y la aprueba como Staff Reserva (pidió Lector)
→ solo ve Reserva (Inicio, selector, Fixture), lee y escribe Reserva, y la
base le rechaza leer/escribir Cuarta, leer usuarios y cambiar la
temporada; con la cuenta abierta, el admin le cambia el rol a Lector desde
afuera (API) → la pantalla pasa sola a ver las 4 categorías sin botones de
edición, y la base le rechaza escribir; le quita el acceso → pasa sola a
"Pedir acceso" → lo pide de nuevo → "pendiente". Modo demo sin
`firebase.js` sigue andando. La cuenta de prueba se borró al final. **Sin
probar**: el mail de "Olvidé mi contraseña" (no se mandaron mails reales).

**2026-10-22 — Datos por temporada (como futdetail).** Decisión de Javi:
guardar por año. Partidos, convocatorias, tabla manual, recordatorios
omitidos, entrenamientos y documentos van bajo `temporadas/<año>/<nodo>/...`
(`NODOS_DE_TEMPORADA`; todo acceso pasa por `dbRef()`, que agrega el prefijo
según `temporadaActual`). Plantel, datos médicos, contratos, préstamos,
multimedia e informes NO dependen del año (son del club / del jugador).
- Selector de Temporada arriba (oculto en Plantel y Reportes, que no
  dependen del año); aviso cuando se mira una que no es la activa. La
  activa y la lista viven en `temporadasInfo` (`activa`, `lista/<año>`);
  `club.json -> temporada.anio` es solo el valor inicial.
- Admin: "Iniciar temporada nueva" en Inicio. No mueve ni borra nada: la
  anterior queda tal cual y se consulta desde el selector. Los ascensos se
  hacen con "Pasar de categoría".
- Distinto de Tigre a propósito: Tigre archiva la temporada en
  `temporadas_cerradas` y deja todo en cero (lo viejo solo se ve desde la
  consola); acá las temporadas viejas se ven en la app.
- Ficha: el historial recorre todas las temporadas. Tabla automática y
  Confiabilidad solo aplican a la temporada activa (los datos de la liga
  son los de hoy).
- Reglas: salen los 6 nodos sueltos, entran `temporadas` y `temporadasInfo`.
- Proyecto de prueba migrado: los datos que estaban en la raíz pasaron a
  `temporadas/2026` (verificado idéntico) con reglas de transición en el
  medio. Probado: arrancar 2027, cargar un partido y convocatoria en 2027,
  volver a 2026 (todo intacto, con aviso), entrenamientos separados por año,
  historial de un jugador con 2026 en Cuarta y 2027 en Quinta, pase de
  categoría ida y vuelta, y la ruta vieja `partidos` ya rechazada por las
  reglas. Después se borró el 2027 de prueba y quedó 2026 como activa.

**2026-10-22 — Segunda pasada por futdetail: todo lo que faltaba.** Se
recorrió lo que no se había visto (Inicio, Estadísticas por división,
Fixture juvenil/reserva, Jugadores Propios, reportes de contratos y
liberados, y las 9 pestañas de la ficha del jugador). Sumado a `index.html`:
- **Inicio** (vista por defecto): resumen de la categoría elegida (PJ/G/E/P/
  GF/GC/% de puntos, últimos 5 partidos, goleadores y asistencias), y de
  todo el club: lesionados actuales, contratos que vencen en 6 meses y
  cumpleaños del mes/de hoy.
- **Estadísticas** por categoría, filtrables por competencia: totales,
  Local/Visitante, sistemas tácticos usados, y por jugador (convocatorias,
  titular, minutos, goles, asistencias, TA, TR, destacado) sumando las
  convocatorias. Resuelve el pendiente de "estadísticas de temporada".
- **Fixture general** (todo el club, juveniles o reserva según `esReserva`):
  una fila por fecha con el resultado de cada categoría y la "Jornada"
  (puntos del club vs. del rival sumando todas las categorías), igual al
  reporte de futdetail.
- **Reportes** (todo el club): liberados/archivados (filtro por fecha y
  posición), jugadores con contrato (filtro por fin de contrato) y
  préstamos/convocatorias vigentes.
- **Plantel**: filtros por nombre (sin importar tildes), posición, edad
  máxima y valoración; columna Edad; orden por posición; y **"Pasar de
  categoría"** a varios jugadores marcados (cambio de temporada) — mueve el
  jugador con el mismo id y sus registros (médicos, contratos, préstamos,
  multimedia, informes) en una sola escritura multi-ruta. Las convocatorias
  quedan en la categoría donde se jugó, con el nombre guardado.
- **Ficha**: ahora se pueden corregir nombre/apellido/posición/nacimiento/
  pie/altura/peso (antes solo al dar de alta), y muestra el historial de
  partidos y estadísticas del jugador recorriendo TODAS las categorías.
- **Datos médicos** (antes "Lesiones"): tipo de consulta (Médica, Física,
  Nutrición, Desarrollo humano, etc.) y, si es lesión, los 9 campos de
  futdetail (registro, causa, tipo, localización, lesión, severidad,
  mecanismo, tratamiento inicial, reincidencia) + fecha real de
  recuperación y estado del tratamiento editables en la tabla, días de baja
  y desvío contra la fecha estimada. "Lesionado" = lesión sin fecha de
  recuperación.
- **Informes** por jugador (Trimestral/Final/Captación, período, URL) —
  nodo nuevo `informes` (sumado a `firebase/rules.example.json`).
- Contratos con observaciones y link; préstamos con link y **notas de
  seguimiento** (`prestamos/<cat>/<id>/notas`).
- Partidos: día del partido (calendario, además del nro de fecha), árbitro,
  y sugerencias de sistema táctico.
- Entrenamientos: se pueden cargar en varias categorías a la vez.

Bugs encontrados y arreglados en el camino:
1. **Textos con comillas se cortaban y se perdían al re-guardar.** Todo dato
   iba directo a `innerHTML`; un `Copa "X"` dentro de `value="..."` quedaba
   en `Copa ` y al guardar de nuevo se pisaba. Ahora todo pasa por `esc()`,
   y los links por `url()` (bloquea `javascript:` y completa `https://`).
2. **La citación PDF listaba a todo el plantel como suplente.** La
   convocatoria guardaba una fila por cada jugador del plantel, convocado o
   no. Ahora hay columna "Conv." y solo se guardan los convocados (marcar
   Titular también lo marca), con el nombre del jugador guardado.
3. **Re-guardar una convocatoria vieja borraba a jugadores archivados o
   pasados de categoría** (no estaban en el plantel, así que no tenían fila,
   y el `.set()` los eliminaba). Ahora aparecen como "fuera del plantel".
4. **Guardados rechazados por Firebase fallaban en silencio.** Ahora un
   cartel rojo avisa cuando la base rechaza un cambio por permisos.
5. Las vistas ocultas seguían escuchando Firebase; ahora al cambiar de
   vista se apagan todas las suscripciones (`apagarSuscripciones`).

Probado contra el Firebase de prueba real (no simulado), desde localhost
con el admin de prueba: ficha con comillas y `<b>` (vuelve intacto),
convocatorias en 2 fechas (14 de 16 guardados, minutos=0 y "sustituido
por" se conservan), citación (11 titulares + 3 suplentes), Estadísticas
(Local/Visitante, por jugador), goleadores en Inicio, historial en la
ficha, lesión → aparece en Inicio → alta → desaparece (29 días, +3 vs.
estimada), consulta de Nutrición (oculta los campos de lesión), contrato
que vence → Inicio y Reportes, préstamo con nota, Fixture general (Jornada
4-1 y 2-2 con Cuarta+Quinta, totales y % verificados a mano), re-editar un
partido desde "Agregar" sin borrar el día ni el Detalle, entrenamiento en
3 categorías, filtros del plantel, rol lector (sin controles de edición),
y celular (375px: sin scroll horizontal de página). Con las reglas nuevas
publicadas en el proyecto de prueba: informe guardado, y pase de 2
jugadores de Cuarta a Quinta (se movieron su lesión, préstamo con nota e
informe; la consulta de otro jugador quedó en Cuarta; la convocatoria vieja
los muestra como "fuera del plantel" y re-guardarla no les borra los goles;
el historial se ve completo desde Quinta). Recorridas todas las vistas en 3
categorías sin errores de consola. Los datos de estas pruebas quedaron en
el Firebase de prueba como demo (Aguirre y Benitez ahora están en Quinta).

**2026-10-02 — Despliegue de prueba real.** Proyecto Firebase
`plataforma-futbol-test` (plan gratuito, Realtime Database + Auth
email/contraseña, reglas de `rules.example.json` publicadas) y sitio en
GitHub Pages (`JaviAguilar1/plataforma-futbol-test`, rama `main`). Para no
romper la regla de oro, la config real (`config/firebase.js`,
`config/club.json`) se commitea SOLO en la rama local `despliegue-prueba`,
que es la que se sube a ese repo — `master` sigue sin credenciales. Datos:
plantel y 10 resultados reales de la 4ta de Tigre (sin fotos), sacados de un
backup local. Usuario admin de prueba creado a mano. Verificado en el sitio
publicado: lectura pública, login, y edición.

**2026-10-02 — Revisión de punta a punta: 5 bugs reales encontrados y
arreglados.** Se armó un simulador de Firebase en JS (guarda, lee y notifica
cambios de verdad, no solo registra qué se llamó) para probar la app con
clics e interacciones reales, no solo con datos sueltos. Bugs encontrados:

1. **`agregarPartido` pisaba el Detalle.** Usaba `.set()` en vez de
   `.update()` — como el formulario de "Agregar" es también la única forma de
   corregir rival/resultado de una fecha ya cargada, volver a usarlo borraba
   competencia/sistema táctico/links/penales/descripción ya guardados desde
   "Detalle". Mismo patrón de bug que ya se había visto en Tigre
   (`saveData` con `.set()` del nodo entero). Arreglado a `.update()`.
2. **`guardarConvocatoria` perdía el 0.** Dorsal y minutos usaban
   `Number(v||0)||null` — si se tipeaba "0" (un suplente que no llegó a
   jugar, minutos=0), el resultado era `null`, indistinguible de "no se
   cargó nada". Además volvía a pedir el plantel a Firebase en vez de leer
   el DOM ya renderizado, con riesgo de romper si un jugador nuevo se
   agregaba entre que se abrió la convocatoria y se guardó. Reescrito para
   leer directo de los inputs en pantalla (`querySelectorAll`) y distinguir
   "vacío" de "cero" (`v===''? null : Number(v)`).
3. **Un jugador archivado seguía apareciendo** en los desplegables de
   "agregar" de Lesiones/Contratos/Préstamos/Multimedia, aunque ya estaba
   oculto en la tabla de Plantel — inconsistente con la idea de "archivado".
   Nuevo helper `idsJugadoresActivos()`, reusado en los 4 lugares.
4. **"Motivo de cambio" guardaba el texto "—" en vez de vacío.** El
   `<option>` de la Convocatoria no tenía `value` explícito, así que el
   navegador usaba el texto visible (el guión "—") como valor real del
   campo vacío. Quedaba guardado en Firebase como el string "—" en vez de
   `null`. Arreglado agregando `value="${m}"`.
5. **"Sustituido por" nunca se restauraba al reabrir la convocatoria.** El
   dato se guardaba bien en Firebase, pero el `<select>` armaba sus
   `<option>` una sola vez sin marcar ninguno como `selected` — al reabrir
   el panel, siempre se veía en blanco aunque el dato estuviera ahí.
   `opcionesSustituto` pasó de ser un string fijo a una función que recibe
   el jugador ya seleccionado.

Probado después de cada arreglo: alta de jugador + ficha completa + archivar
(desaparece de Plantel pero no de los desplegables de registros viejos),
cambio de categoría (sigue sin mezclar datos, bug de Fase inicial sigue
resuelto con las 5 suscripciones nuevas de Plantel), partido + Detalle +
re-edición sin pérdida de datos, convocatoria con minutos=0 + roja con sus 4
sub-campos + round-trip completo (cerrar y reabrir, los valores vuelven tal
cual), Confiabilidad (avisa partido sin cargar, recordatorio de link
faltante + Omitir), Tabla de posiciones manual, Documentos/Entrenamientos
con roles (un "lector" ve los datos pero no los formularios ni Borrar), rol
con categoría específica (puede editar Reserva, no Cuarta). Sin errores de
consola en ningún paso. Lado Python: compila todo sin cambios.

**2026-10-02 — Catálogo completo de campos de futdetail.** Se terminó de
recorrer futdetail (se había cortado a medias por una caída de sesión/login
intermedia) incluyendo lo que faltaba: Planificación, Entrenamientos,
Proyectos Externos, Detalle de Resultados (reporte, sin campos nuevos),
Multimedia, Préstamos, Convocatorias a Selección, y el selector de columnas
de "Listado de Jugadores" (reveló el catálogo completo de campos del
jugador de una sola vez). Sumado a `index.html`:
- **Ficha de jugador:** Perfil, Valoración (Excelente/Muy buena/Buena/
  Regular), Archivado + Fecha liberado (en vez de borrar un jugador se
  archiva — igual criterio que futdetail con "Jug. Eliminados"/"Liberados";
  oculto por default en el Plantel, con checkbox para mostrarlo), y el
  Nombre de representante/padre/madre (antes solo tenían email/teléfono).
- **Lesiones:** se sumaron Diagnóstico ("Lesión"), Tipo de lesión y
  Localización — antes solo observaciones + fecha estimada de recuperación.
- **Contratos:** se sumó Fecha de inicio (antes solo fecha de fin).
- **Convocatoria:** se sumó Asistencias, y la tarjeta roja pasó de un
  checkbox simple a sus 4 sub-campos reales de futdetail (fecha de
  expulsión, link, PDF, observaciones).
- **Dos secciones nuevas en Plantel:** Préstamos/Convocatorias a selección
  (mismo formulario en futdetail para las dos cosas, un campo `tipo` las
  distingue) y Multimedia (clips individuales por jugador).
- **Pestaña nueva "Recursos"** con Documentos (Planificación + Proyectos
  Externos + Rendimiento Físico unificados — en futdetail los 3 comparten
  exactamente el mismo formulario simple de título/fecha/descripción/url) y
  Entrenamientos (fecha, descripción, etiquetas, y 3 links: campo, arqueros,
  planificación).
- `firebase/rules.example.json` actualizado con los 4 nodos nuevos
  (`prestamos`, `multimedia`, `documentos`, `entrenamientos`).
- Probado con datos falsos: filtro de archivados (oculto por default,
  aparece con el checkbox), ficha completa guarda los campos nuevos (`db`
  simulado), convocatoria guarda asistencias y los 4 sub-campos de la roja,
  Documentos/Entrenamientos/Préstamos/Multimedia renderizan y guardan bien
  — y la pestaña Recursos probada de punta a punta en el navegador (clic
  real en el botón del nav). Sin probar contra Firebase real todavía, como
  el resto del proyecto.

**2026-10-02 — Fase 4: roles por categoría, Confiabilidad, export PDF.**
Evaluando qué de Tigre aplica a un club genérico y qué no:

- **Roles finos:** `club.json -> roles` pasó de lista de strings a lista de
  objetos `{id, nombre, categorias}` — `categorias` es `"todas"`, una lista
  de `categoria.id`, o `[]` (solo lectura). `puedeEditar(catId?)` en
  `index.html` ahora respeta eso (default a `categoriaActual` si no se pasa
  nada, así ningún call site existente tuvo que tocarse). Permite dar de
  alta, por ejemplo, un staff que solo edita Reserva.
- **Bug real encontrado y corregido:** el adaptador de liga escribía
  `data/tablas.json` (archivo estático) pero `index.html` leía la tabla de
  posiciones SIEMPRE de Firebase (`tablaPosiciones`) — con un adaptador
  configurado, el scraper corría pero la pantalla nunca se enteraba. Ahora
  `renderTabla()` lee `data/tablas.json` cuando el adapter no es `"manual"`
  (con botón "Actualizar"), y `scrape_main.py` también pide
  `fetch_fixture` (antes solo pedía la tabla de posiciones, nunca el
  fixture) y lo guarda en el mismo archivo bajo `"fixture"`.
- **Confiabilidad** (botón nuevo en el nav, solo aparece si hay un adaptador
  de liga real configurado — sin fuente automática no hay nada que cruzar):
  compara partidos cargados a mano contra el fixture de `data/tablas.json`
  (resultado discrepante, o partido que la liga ya tiene y falta cargar),
  suma PJ/PG/PE/PP/GF/GC de los partidos propios y lo compara contra la fila
  del club en la tabla de la liga (busca por `nombreEquipoEnLiga`), y avisa
  de partidos jugados sin ningún link cargado (con "Omitir", guardado en
  `recordatoriosOmitidos/<cat>/<fecha>`). Son los 3 cruces de los 5 de Tigre
  que tienen sentido con lo que existe acá — los otros dos (goleadores y
  links vs. futdetail) no aplican porque no hay ningún "futdetail" genérico
  con el que cruzar.
- **Export a PDF:** ficha de jugador (botón "PDF" en cada fila de
  Plantel) y citación/convocatoria con espacio para firma (botón dentro de
  Convocatoria) — mismo patrón sin librerías que ya usa Tigre (ventana
  nueva + `window.print()`).
- **Video sync, EXCLUIDO a propósito:** depende por completo de cómo cada
  club filma y sube sus partidos (en Tigre: streams de YouTube, calibración
  contra el cartel o el corte de edición) — no hay una versión genérica
  razonable sin conocer ese flujo real. Revisar si/cuándo el club real lo
  necesite y confirme cómo filma.
- **Reglas de Firebase de ejemplo** (`firebase/rules.example.json`)
  actualizadas con los nodos que se fueron sumando y que no estaban
  cubiertos (`lesiones`, `contratos`, `convocatorias`,
  `recordatoriosOmitidos`).
- Probado: roles con categorías (incluye rol inexistente → false, categoría
  explícita vs. `categoriaActual`), Confiabilidad con datos falsos (detecta
  discrepancia de resultado, partido sin cargar, y diferencia de tabla
  propia), export de ficha y de citación (con `db`/`window.open` simulados,
  arma el HTML esperado) — y de punta a punta en el navegador real: con un
  `club.json`/`data/tablas.json` de prueba (no comiteados), la Tabla de
  posiciones mostró la fila que vino del archivo estático.

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
- Fase 4 (resto) — video sync queda afuera hasta saber cómo filma el club
  real; si en algún momento se suma, no reusar el de Tigre tal cual (está
  atado a YouTube + Catapult con su calibración específica).
- Sin probar NADA de esto (desde Fase 1) contra un club real todavía —
  todo lo automático (Catapult, adaptadores de liga) está verificado con
  datos de prueba armados a mano, no con cuentas/sitios reales.
