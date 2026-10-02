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
  realmente use.
- **fuentes.liga.adapter**: nombre del archivo en
  `scripts/adapters/liga/` (sin `.py`) que trae tabla de posiciones/fixture
  de la liga real. `"manual"` = no hay scraper, se carga todo a mano en la
  app (válido como punto de partida).
- **fuentes.gps.adapter**: ídem para GPS — nombre del archivo en
  `scripts/adapters/gps/`. `"csv_generico"` ya funciona sin configurar nada
  más (ver ese archivo). Los demás (`catapult`, `kinexon`, `statsports`,
  `wimu`) son stubs: hay que completarlos cuando se sepa el proveedor real
  del club y se tengan credenciales para probar.

# `firebase.js` — credenciales reales (no va a git)

Copiá `firebase.example.js` a `firebase.js` con el `firebaseConfig` que te da
la consola de Firebase para el proyecto de ESE club.
