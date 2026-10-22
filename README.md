# Plataforma de seguimiento de fútbol (plantilla genérica)

Plantilla para armar, por club, una app de seguimiento de plantel, partidos,
tabla de posiciones y rendimiento físico (GPS). Cada club que la use tiene su
**propia copia** (repo + Firebase propios) — esto no es un sistema multi-club.

Nace como generalización de la app de Tigre Juveniles, pensada para poder
ofrecerse a otro club sin arrastrar nombres, colores ni datos de Tigre.

## Cómo poner en marcha una instancia para un club nuevo

1. **Cloná este repo** (o copialo) a una carpeta/repo nuevo para ese club.
2. **Config del club:** copiá `config/club.example.json` → `config/club.json`
   y completá nombre, colores, categorías/divisiones, duración de los
   tiempos, posiciones y qué adaptador de liga/GPS vas a usar. Ver
   `config/README.md` para el detalle de cada campo.
3. **Firebase:** creá un proyecto de Firebase propio para ese club
   (Realtime Database + Authentication con email/contraseña), copiá
   `config/firebase.example.js` → `config/firebase.js` con las credenciales
   reales, y publicá las reglas de `firebase/rules.example.json` (no hace
   falta tocarlas: leen los permisos de cada rol de la base).
4. **Primer admin:** publicá la app (GitHub Pages u otro hosting estático),
   creá tu cuenta desde "Crear cuenta" y, en la consola de Firebase, poné
   `users/<tu uid>/role` = `"admin"`. De ahí en más las cuentas se aprueban
   desde la pestaña Usuarios.
5. **Fuente de liga (datos de rivales):** `"manual"` funciona de entrada. Si
   la liga publica tabla/fixture en su sitio, `generic_html_table` o
   `generic_json_api` (en `scripts/adapters/liga/`) lo traen; si no, se
   escribe un adaptador nuevo con la misma interfaz.
6. **GPS:** se puede cargar desde la app subiendo el CSV que exporta
   cualquier proveedor. Para carga automática: `catapult` (por API) o
   `csv_generico` (lee una carpeta), con una cuenta de rol `importador`.
7. **Carga automática y backup** (en una compu del club, tarea programada):
   `python scripts/scrape_main.py` (liga + GPS) y
   `python scripts/backup_firebase.py` (backup diario fuera del repo).

Todo el detalle de cada paso está en `config/README.md`.

## Estructura

```
config/              configuración del club (real, fuera de git) + ejemplos
index.html           la app completa (una sola página)
firebase/            reglas de seguridad (generadas por scripts/generar_reglas.py)
scripts/
  scrape_main.py     liga -> data/tablas.json, GPS -> Firebase
  backup_firebase.py backup diario de la base (fuera del repo)
  generar_reglas.py  arma firebase/rules.example.json
  firebase_rest.py   acceso a Firebase compartido por los scripts
  adapters/liga/     interfaz + adaptadores de tabla/fixture de la liga
  adapters/gps/      interfaz + CSV genérico + Catapult (+ stubs por proveedor)
data/                tabla/fixture de la liga (datos públicos)
```

## Por qué "por club" y no multi-club

Decisión tomada a propósito: cada club tiene su propio Firebase y su propio
despliegue. Es más simple de permisos/seguridad (no hay riesgo de que un
club vea datos de otro) y es el mismo patrón que ya funciona en Tigre.
