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
3. **Firebase:** creá un proyecto de Firebase (Realtime Database) propio para
   ese club, copiá `config/firebase.example.js` → `config/firebase.js` con
   las credenciales reales, y aplicá las reglas de `firebase/rules.example.json`
   (ajustadas a los roles que hayas puesto en `club.json`).
4. **Fuente de liga (datos de rivales):** `scripts/adapters/liga/` tiene la
   interfaz (`base.py`) y un ejemplo de scraping de tabla HTML
   (`generic_html_table.py`). Si la liga del club nuevo tiene un sitio
   parecido, se adapta ese archivo; si no, se escribe un adaptador nuevo que
   cumpla la misma interfaz.
5. **GPS:** `scripts/adapters/gps/` tiene la interfaz (`base.py`) y un
   importador de CSV/Excel genérico ya funcional
   (`csv_generico.py`) que sirve para cualquier proveedor que solo exporte
   archivo. Para los que tienen API propia (Catapult, Kinexon) hay un stub
   documentado con lo que hace falta para terminarlo — ver cada archivo.
6. **Corré el scraper** (`scripts/scrape_main.py`) para generar
   `data/tablas.json`, y abrí `index.html` (servido como sitio estático,
   igual que la app de Tigre).

## Estructura

```
config/            configuración del club (real, fuera de git) + ejemplos
index.html         la app (plantel, partidos, tabla de posiciones)
firebase/          reglas de seguridad de ejemplo
scripts/
  scrape_main.py   orquesta los adaptadores y genera data/tablas.json
  adapters/liga/   interfaz + adaptador de ejemplo para datos de rivales/liga
  adapters/gps/    interfaz + importador CSV genérico + stubs por proveedor
data/              salida generada (no se commitea el archivo real del club)
```

## Por qué "por club" y no multi-club

Decisión tomada a propósito: cada club tiene su propio Firebase y su propio
despliegue. Es más simple de permisos/seguridad (no hay riesgo de que un
club vea datos de otro) y es el mismo patrón que ya funciona en Tigre.
