# `club.json` — config real del club (no va a git)

Copiá `club.example.json` a `club.json` y completá:

- **club**: nombre, escudo (URL) y colores (variables CSS de la app: fondo,
  superficie de tarjetas, color primario/acento, color de texto).
- **temporada.anio**: temporada con la que arranca la instancia. Solo se usa
  mientras la base no tenga `temporadasInfo/activa`; de ahí en adelante la
  temporada activa la cambia el admin desde Inicio ("Iniciar temporada
  nueva"). Partidos, convocatorias, tabla, recordatorios, entrenamientos y
  documentos se guardan por año (`temporadas/<año>/...`) y las temporadas
  anteriores se consultan con el selector de arriba; el plantel y lo del
  jugador (datos médicos, contratos, préstamos, multimedia, informes) es del
  club y no depende del año.
- **temporada.categorias**: una entrada por categoría/división del club. El
  `id` es interno (se usa como clave en Firebase, no se muestra), `nombre` es
  lo que ve el usuario. `duracionTiempoMin` importa para todo lo que mida
  partidos en minutos (si en el futuro se suma GPS/video sync, como en
  Tigre). `esReserva` + `semestres` es para categorías que juegan por
  semestre en vez de por fecha de temporada completa (ajustá o sacá si el
  club nuevo no tiene ese caso).
- **roles**: lista de roles que puede tener un usuario. Cada uno es
  `{ "id": "...", "nombre": "...", "categorias": ..., "ve": ... }`:
  - `categorias`: qué categorías puede EDITAR (`"todas"`, una lista de
    `categoria.id`, o `[]` para solo lectura).
  - `ve`: qué categorías puede VER (mismo formato; si no está, ve todas).
    Ej.: `"staffReserva"` ve y edita solo Reserva.
  - **Tiene que haber un rol con id `"admin"`**: es el que aprueba usuarios,
    inicia temporadas y ve/edita todo. Las reglas de Firebase lo reconocen
    por ese id.
  - Las reglas de Firebase no pueden leer este archivo: cada vez que el
    admin entra a la app, se copian los permisos de cada rol al nodo
    `rolesConfig` de la base, y las reglas controlan con eso categoría por
    categoría. **Después de cambiar roles acá, el admin tiene que entrar
    una vez** para que la base se entere.

  **Cuentas:** sin cuenta aprobada no se ve nada. La persona entra a la app,
  toca "Crear cuenta", elige su función y queda pendiente; el admin la
  aprueba (o le cambia el rol, o la rechaza) en la pestaña "Usuarios", que
  muestra cuántas hay pendientes. La pantalla de la persona se habilita sola
  al aprobarla. **El primer admin** se crea a mano una sola vez: crear la
  cuenta desde la app y, en la consola de Firebase → Realtime Database,
  agregar `users/<uid>/role` = `"admin"`.
- **posiciones**: catálogo de posiciones para la ficha de jugador. El default
  salió de relevar un sistema real de gestión de clubes (futdetail), es un
  catálogo estándar de fútbol — no hace falta tocarlo salvo que el club use
  otra nomenclatura.
- **disciplina**: reglas de amarillas acumuladas de la liga del club.
  `amarillasAlerta` (desde cuántas avisa), `amarillasSuspension` (con cuántas
  cumple una fecha; el conteo vuelve a cero ahí o con una expulsión) y
  `competenciasQueNoCuentan` (nombres de competencia, tal cual se cargan en
  el partido, cuyas tarjetas no suman — ej. amistosos). Se ve en Inicio y
  como aviso al lado de cada jugador en la Convocatoria. Si falta, usa 4 y 5.
- **linksPartido**: qué tipos de link se pueden cargar por partido (video,
  resumen, análisis, informe, etc.). Sacá o agregá según lo que el club
  realmente use — si agregás una clave nueva, sumale también su etiqueta en
  `ETIQUETAS_LINK` dentro de `index.html` (si no, se muestra la clave cruda).
- **fuentes.liga.adapter**: nombre del archivo en
  `scripts/adapters/liga/` (sin `.py`) que trae tabla de posiciones/fixture
  de la liga real. `"manual"` = no hay scraper, se carga todo a mano en la
  app (válido como punto de partida). Los otros dos ya están terminados
  (ver más abajo): `"generic_html_table"` (la liga publica una `<table>`
  HTML común) y `"generic_json_api"` (la liga la dibuja con JavaScript a
  partir de un endpoint JSON propio).
- **fuentes.gps.adapter**: ídem para la carga automática de GPS — nombre
  del archivo en `scripts/adapters/gps/` (la carga desde la app con CSV no
  necesita esto, ver "GPS" más abajo). `"csv_generico"` lee los CSV de una
  carpeta con `mapeoColumnas` (ver ese archivo). `"catapult"` también está terminado (ver abajo).
  Los demás (`kinexon`, `statsports`, `wimu`) son stubs: no encontramos
  documentación pública de API confiable para ninguno de los tres — si el
  club nuevo usa alguno, lo más rápido es arrancar con `csv_generico`
  apuntando a lo que ese software exporte.

## Qué guarda cada parte de la app (Firebase)

Todo nace vacío — no hace falta crear estos nodos a mano, los arma la app
sola al guardar algo por primera vez.

- `plantel/<categoria>/<id>`: ficha completa del jugador (datos generales +
  perfil/valoración + archivado/fecha liberado + contacto + nombre/email/
  teléfono de representante, padre y madre) — ver "Ver ficha" en cada fila.
  Un jugador "archivado" no se borra (nunca se pisa historial): queda oculto
  por default, con un checkbox "Mostrar jugadores archivados" para verlo.
- `lesiones/<categoria>/<id>`: jugador, fecha, diagnóstico, tipo de lesión,
  localización, observaciones, fecha estimada de recuperación.
- `contratos/<categoria>/<id>`: jugador, fecha de inicio, fecha de fin
  (calcula "meses restantes" solo).
- `prestamos/<categoria>/<id>`: jugador, tipo ("Préstamo a otro club" o
  "Convocatoria a selección" — mismo concepto, un solo campo `tipo` los
  distingue), club o selección, fecha inicio/fin, observaciones.
- `multimedia/<categoria>/<id>`: clips individuales por jugador (fecha,
  descripción, link, observaciones) — ej. "Individual vs Rival Fecha 5".
- `partidos/<categoria>/<fechaNro>`: resultado + "Detalle" (competencia,
  sistema táctico, planes de juego, penales, descripción, links) +
  "Convocatoria" (titular/suplente, dorsal, minutos, goles, asistencias,
  amarilla/roja —con fecha de expulsión, link, PDF y observaciones propias
  de la roja—, a quién sustituyó, motivo del cambio y jugador destacado; un
  registro por jugador del plantel).
- `documentos/<categoria>/<id>`: Planificación, Proyectos externos y
  Rendimiento físico unificados (mismo patrón simple en los tres: tipo,
  título, microciclo opcional, fecha desde/hasta, descripción, url a un
  documento externo — típicamente Drive).
- `entrenamientos/<categoria>/<id>`: por semana — fecha, descripción,
  etiquetas, y 3 links (entrenamiento de campo, de arqueros, planificación).
- `tablaPosiciones/<categoria>`: manual o escrita por el adaptador de liga.

No hay (todavía) ninguna pantalla que SUME estos datos en una estadística de
temporada por jugador (convocatorias/PJ/goles/etc. acumulados) — hoy se ven
partido por partido en la Convocatoria. Si hace falta, se puede calcular
leyendo todas las fechas de `convocatorias/<categoria>/*` para un jugador.

## Adaptadores de liga (datos de rivales)

### generic_html_table — la liga publica una `<table>` HTML

```json
"fuentes": {
  "liga": {
    "adapter": "generic_html_table",
    "config": {
      "urls": { "<categoria.id>": "https://liga.com/posiciones-categoria" },
      "urlsFixture": { "<categoria.id>": "https://liga.com/fixture-categoria" },
      "nombreEquipoEnLiga": "Nombre EXACTO del club tal cual figura en esa tabla"
    }
  }
}
```

Busca, dentro de todas las `<table>` de la página, la que tenga pinta de
tabla de posiciones (columnas Equipo/PJ/PG/PE/PP/GF/GC/Pts) o de fixture
(Fecha/Local/Visitante/Resultado) — no hace falta que sea exactamente esos
nombres, reconoce alias razonables. `urlsFixture` puede omitirse si es la
misma URL que `urls`. Si la página arma la tabla con JavaScript (sin
`<table>` en el HTML crudo, como le pasa a la Reserva de Tigre con el widget
de Opta), este adaptador no sirve — hay que mirar si el sitio tiene un
endpoint JSON (ver el adaptador siguiente) o escribir uno nuevo.

### generic_json_api — la liga la arma con JavaScript desde un endpoint JSON

```json
"fuentes": {
  "liga": {
    "adapter": "generic_json_api",
    "config": {
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
  }
}
```

El endpoint se encuentra abriendo la página real de la liga, F12 → pestaña
Red/Network, filtrando por XHR/Fetch y mirando qué request trae la tabla o
el fixture. Las rutas (`"team.name"`, `"score.fullTime.home"`, etc.) navegan
el JSON real de esa respuesta — se arman mirándolo una sola vez, sin
programar nada. Ver el docstring de
`scripts/adapters/liga/generic_json_api.py` para más detalle (incluye el
caso de un marcador como texto único en vez de dos campos separados).

## GPS

Hay dos formas de cargar sesiones; las dos terminan en el mismo lugar
(`temporadas/<año>/gps/<categoría>/<sesión>` en Firebase, detrás del muro de
ingreso) y se ven en la pestaña **GPS** y en la ficha de cada jugador:

1. **Desde la app (sin configurar nada):** pestaña GPS → "Cargar sesión
   desde CSV". Sirve para cualquier proveedor, porque todos exportan CSV. La
   app adivina qué columna es cada dato, se puede corregir, y lo recuerda
   para la próxima. Si `fuentes.gps.config.mapeoColumnas` está cargado, lo
   usa como punto de partida.
2. **Automática** (`python scripts/scrape_main.py`, con un adaptador por API
   como `catapult`, o `csv_generico` leyendo una carpeta): sube las sesiones
   de los últimos 14 días (repetirlo no duplica). Necesita
   `IMPORTADOR_EMAIL` / `IMPORTADOR_PASSWORD` de una cuenta con rol
   `"importador"` (se crea igual que la de backup: cuenta desde la app y
   `users/<uid>/role` = `"importador"` en la consola). Ese rol solo puede
   escribir sesiones de GPS, nada más.

**Nombres:** se guarda el nombre tal cual lo trae el proveedor y la app lo
vincula con el plantel sola (nombre y apellido, inicial + apellido, sin
importar tildes ni mayúsculas). Los que no reconoce aparecen "sin vincular"
con un selector para elegir el jugador una vez; queda guardado en
`gpsAlias/<categoría>` para las cargas siguientes.

### Catapult

```json
"fuentes": {
  "gps": {
    "adapter": "catapult",
    "config": {
      "equipos": { "Nombre del equipo en Catapult": "<categoria.id>" },
      "soloPartidos": true
    }
  }
}
```

El nombre del equipo se saca entrando a OpenField con la cuenta del club y
mirando cómo están cargados los equipos ahí (tiene que ser texto idéntico).
Las credenciales NUNCA van acá: se setean como variables de entorno
`CATAPULT_EMAIL` / `CATAPULT_PASSWORD` donde corra `scripts/scrape_main.py`
(secret de GitHub Actions, o variable de entorno en la PC del club — mismo
patrón que ya usa Tigre con sus credenciales de futdetail).

# `firebase.js` — credenciales reales (no va a git)

Copiá `firebase.example.js` a `firebase.js` con el `firebaseConfig` que te da
la consola de Firebase para el proyecto de ESE club.

# Reglas de seguridad de Firebase

`firebase/rules.example.json` se pega a mano en la consola de Firebase
(Realtime Database → Reglas → Publicar). No se edita a mano: lo genera
`python scripts/generar_reglas.py` (la condición "este rol puede ver /
editar esta categoría" se repite en cada nodo). Nada se puede leer sin un rol
aprobado, cada rol ve y edita solo sus categorías, y nadie puede asignarse un
rol a sí mismo (solo el admin escribe `role`). **Cada vez que se actualiza
`index.html` a una versión que suma un nodo nuevo** (ej. `informes`), hay que
volver a publicar las reglas: sin la regla, Firebase rechaza la lectura y la
escritura de ese nodo (la app lo avisa con un cartel rojo abajo, y acciones
que leen varios nodos — como "Pasar de categoría" — no se completan).

# Backup diario (en la compu del club)

`scripts/backup_firebase.py` baja la base entera a un JSON por día, en una
carpeta **fuera del repo** (tiene datos personales y médicos: el script se
niega a guardar adentro del repo). Por defecto en
`Documentos\backups-<projectId>`, conserva los últimos 60.

1. Crear una cuenta para el backup desde la app ("Crear cuenta", con un mail
   del club) y, en la consola de Firebase → Realtime Database, ponerle
   `users/<uid>/role` = `"backup"`. Ese rol puede leer toda la base pero no
   escribir nada.
2. En la compu del club (una sola vez, en una terminal):
   ```
   setx BACKUP_EMAIL "backup@tuclub.com"
   setx BACKUP_PASSWORD "la-contraseña-de-esa-cuenta"
   schtasks /Create /SC DAILY /ST 03:00 /TN "Backup club" /TR "python C:\ruta\al\repo\scripts\backup_firebase.py"
   ```
   Opcionales: `BACKUP_DIR` (otra carpeta, ej. una sincronizada con Drive) y
   `BACKUP_CONSERVAR` (cuántos días guardar).
3. Probarlo: `schtasks /Run /TN "Backup club"` y fijarse que aparezca el
   archivo del día.

**Restaurar:** consola de Firebase → Realtime Database → menú ⋮ → "Importar
JSON" con el archivo del día elegido. **Reemplaza la base entera**: bajar
antes un backup del estado actual por las dudas.

Si el club pasa al plan pago de Firebase (Blaze), también puede activar los
backups automáticos de la propia consola.
