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
- **roles**: lista de roles que puede tener un usuario logueado. El primero
  de la lista es el único con permiso total (equivalente a "admin"); el resto
  los interpreta la app como "puede editar pero no administrar usuarios" —
  ajustar en `index.html` si el club necesita algo más fino.
- **posiciones**: catálogo de posiciones para la ficha de jugador. El default
  salió de relevar un sistema real de gestión de clubes (futdetail), es un
  catálogo estándar de fútbol — no hace falta tocarlo salvo que el club use
  otra nomenclatura.
- **linksPartido**: qué tipos de link se pueden cargar por partido (video,
  resumen, análisis, informe, etc.). Sacá o agregá según lo que el club
  realmente use — si agregás una clave nueva, sumale también su etiqueta en
  `ETIQUETAS_LINK` dentro de `index.html` (si no, se muestra la clave cruda).

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
partido por partido en la Convocatoria. Si hace falta, se puede calcular leyendo
todas las fechas de `convocatorias/<categoria>/*` para un jugador.
- **fuentes.liga.adapter**: nombre del archivo en
  `scripts/adapters/liga/` (sin `.py`) que trae tabla de posiciones/fixture
  de la liga real. `"manual"` = no hay scraper, se carga todo a mano en la
  app (válido como punto de partida).
- **fuentes.gps.adapter**: ídem para GPS — nombre del archivo en
  `scripts/adapters/gps/`. `"csv_generico"` ya funciona sin configurar nada
  más (ver ese archivo). `"catapult"` también está terminado (ver abajo).
  Los demás (`kinexon`, `statsports`, `wimu`) son stubs: no encontramos
  documentación pública de API confiable para ninguno de los tres — si el
  club nuevo usa alguno, lo más rápido es arrancar con `csv_generico`
  apuntando a lo que ese software exporte.

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
