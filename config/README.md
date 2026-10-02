# `club.json` — config real del club (no va a git)

Copiá `club.example.json` a `club.json` y completá:

- **club**: nombre, escudo (URL) y colores (variables CSS de la app: fondo,
  superficie de tarjetas, color primario/acento, color de texto).
- **temporada.categorias**: una entrada por categoría/división del club. El
  `id` es interno (se usa como clave en Firebase, no se muestra), `nombre` es
  lo que ve el usuario. `duracionTiempoMin` importa para todo lo que mida
  partidos en minutos (si en el futuro se suma GPS/video sync, como en
  Tigre). `esReserva` + `semestres` es para categorías que juegan por
  semestre en vez de por fecha de temporada completa (ajustá o sacá si el
  club nuevo no tiene ese caso).
- **roles**: lista de roles que puede tener un usuario logueado. Cada uno es
  `{ "id": "...", "nombre": "...", "categorias": "todas" | ["CAT1","CAT2"] | [] }`.
  `id` es lo que se guarda en `users/<uid>/role` (asignado a mano desde la
  consola de Firebase, no hay pantalla para esto — mismo criterio que Tigre);
  `nombre` es lo que se muestra; `categorias` define qué puede EDITAR ese rol
  (`"todas"`, una lista de `categoria.id`, o `[]` para un rol de solo
  lectura). El primero de la lista es el único que cuenta como "admin"
  (`esAdmin()` en `index.html` — hoy no hay ninguna acción que dependa de
  eso, queda para cuando haga falta distinguir "puede editar" de "puede
  administrar usuarios"). Sirve para dar de alta, por ejemplo, un staff que
  solo tiene que tocar una categoría (ver `"staffReserva"` en el ejemplo).
- **posiciones**: catálogo de posiciones para la ficha de jugador. El default
  salió de relevar un sistema real de gestión de clubes (futdetail), es un
  catálogo estándar de fútbol — no hace falta tocarlo salvo que el club use
  otra nomenclatura.
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
- **fuentes.gps.adapter**: ídem para GPS — nombre del archivo en
  `scripts/adapters/gps/`. `"csv_generico"` ya funciona sin configurar nada
  más (ver ese archivo). `"catapult"` también está terminado (ver abajo).
  Los demás (`kinexon`, `statsports`, `wimu`) son stubs: no encontramos
  documentación pública de API confiable para ninguno de los tres — si el
  club nuevo usa alguno, lo más rápido es arrancar con `csv_generico`
  apuntando a lo que ese software exporte.

## Qué guarda cada parte de la app (Firebase)

Todo nace vacío — no hace falta crear estos nodos a mano, los arma la app
sola al guardar algo por primera vez.

- `plantel/<categoria>/<id>`: ficha completa del jugador (datos generales +
  contacto + representante/padre/madre) — ver "Ver ficha" en cada fila.
- `lesiones/<categoria>/<id>` y `contratos/<categoria>/<id>`: tablas simples
  debajo del plantel, cada registro apunta a un `jugadorId` del plantel.
- `partidos/<categoria>/<fechaNro>`: resultado + "Detalle" (competencia,
  sistema táctico, planes de juego, penales, descripción, links) +
  "Convocatoria" (titular/suplente, dorsal, minutos, goles, tarjetas,
  cambios y jugador destacado, un registro por jugador del plantel).
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

## Adaptadores de GPS

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
