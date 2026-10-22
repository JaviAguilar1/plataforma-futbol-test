"""Acceso a la base de Firebase por REST desde los scripts (backup, importador).

Usa el mismo config/firebase.js de la app (apiKey y databaseURL son públicos)
y se loguea con email/contraseña de una cuenta con rol: las reglas no dejan
leer ni escribir nada sin sesión.
"""
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parent.parent


def leer_config_firebase():
    texto = (RAIZ_REPO / "config" / "firebase.js").read_text(encoding="utf-8")
    campo = lambda k: re.search(rf'{k}\s*:\s*"([^"]+)"', texto).group(1)
    return campo("apiKey"), campo("databaseURL").rstrip("/"), campo("projectId")


def pedir_json(url, cuerpo=None, metodo=None):
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8") or "null")


def login(api_key, email, password):
    return pedir_json(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}",
        {"email": email, "password": password, "returnSecureToken": True},
    )["idToken"]


def slug_nombre(nombre):
    """Igual que slugNombre() de index.html: así la app reconoce lo que sube el importador."""
    sin_acentos = "".join(c for c in unicodedata.normalize("NFD", str(nombre)) if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "_", sin_acentos).strip("_")
