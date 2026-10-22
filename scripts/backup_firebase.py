"""Backup completo de la base de Firebase del club a una carpeta PRIVADA.

Corre en la compu del club (tarea programada, ver config/README.md). Se
loguea con una cuenta de rol "backup" (las reglas le dejan leer toda la base
pero no escribir nada) y baja la base entera en un JSON, listo para
restaurar con "Importar JSON" en la consola de Firebase.

NUNCA guardar los backups dentro del repo: tienen datos personales y médicos
de los jugadores (el script se niega si la carpeta destino está adentro).

Variables de entorno:
  BACKUP_EMAIL / BACKUP_PASSWORD  cuenta con rol "backup" (obligatorias)
  BACKUP_DIR        carpeta destino (default: Documentos/backups-<projectId>)
  BACKUP_CONSERVAR  cuántos backups diarios guardar (default 60)
"""
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parent.parent


def leer_config_firebase():
    texto = (RAIZ_REPO / "config" / "firebase.js").read_text(encoding="utf-8")
    campo = lambda k: re.search(rf'{k}\s*:\s*"([^"]+)"', texto).group(1)
    return campo("apiKey"), campo("databaseURL").rstrip("/"), campo("projectId")


def pedir_json(url, cuerpo=None):
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fallar(mensaje):
    print(f"[ERROR] {mensaje}")
    sys.exit(1)


def main():
    email, password = os.environ.get("BACKUP_EMAIL"), os.environ.get("BACKUP_PASSWORD")
    if not email or not password:
        fallar("faltan las variables de entorno BACKUP_EMAIL / BACKUP_PASSWORD.")

    api_key, db_url, project_id = leer_config_firebase()
    carpeta = Path(os.environ.get("BACKUP_DIR") or Path.home() / "Documents" / f"backups-{project_id}").resolve()
    if carpeta == RAIZ_REPO or RAIZ_REPO in carpeta.parents:
        fallar(f"la carpeta de backups ({carpeta}) esta dentro del repo: elegir una fuera (BACKUP_DIR).")
    conservar = int(os.environ.get("BACKUP_CONSERVAR") or 60)

    try:
        token = pedir_json(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}",
            {"email": email, "password": password, "returnSecureToken": True},
        )["idToken"]
        base = pedir_json(f"{db_url}/.json?auth={token}")
    except urllib.error.HTTPError as e:
        detalle = " ".join(e.read().decode("utf-8", errors="replace").split())[:300]
        fallar(f"login o lectura rechazados ({e.code}): {detalle}. Revisar que la cuenta exista y tenga rol \"backup\".")
    except urllib.error.URLError as e:
        fallar(f"sin conexion con Firebase: {e.reason}")

    if not isinstance(base, dict) or not base:
        fallar("la base vino vacia: no se guarda un backup vacio.")

    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / f"backup-{datetime.date.today().isoformat()}.json"
    destino.write_text(json.dumps(base, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    print(f"[OK] backup guardado en {destino} ({destino.stat().st_size // 1024} KB, nodos: {', '.join(sorted(base))})")

    for viejo in sorted(carpeta.glob("backup-*.json"))[:-conservar]:
        viejo.unlink()
        print(f"[OK] backup viejo borrado: {viejo.name}")


if __name__ == "__main__":
    main()
