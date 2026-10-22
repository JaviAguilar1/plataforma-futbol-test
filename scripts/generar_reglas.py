"""Genera firebase/rules.example.json.

Las reglas se escriben con este script porque la condición de "puede ver /
editar esta categoría" se repite en cada nodo y es larga. Correr después de
sumar un nodo nuevo:  python scripts/generar_reglas.py
"""
import json
from pathlib import Path

ROL = "root.child('users').child(auth.uid).child('role').val()"
ES_ADMIN = f"auth != null && {ROL} === 'admin'"
TIENE_ROL = "auth != null && root.child('users').child(auth.uid).child('role').exists()"
PROPIO = "auth != null && auth.uid === $uid"
SIN_ROL_AUN = "!root.child('users').child($uid).child('role').exists()"


def permiso(tipo):
    """tipo = 've' o 'edita'; se lee de rolesConfig/<rol>/<tipo> ('todas' o {CAT: true})."""
    cfg = f"root.child('rolesConfig').child({ROL}).child('{tipo}')"
    return f"auth != null && ({ROL} === 'admin' || {cfg}.val() === 'todas' || {cfg}.child($cat).val() === true)"


POR_CATEGORIA = {"$cat": {".read": permiso("ve"), ".write": permiso("edita")}}

# Del club / del jugador (no dependen de la temporada).
NODOS_CLUB = ["plantel", "lesiones", "contratos", "prestamos", "multimedia", "informes"]

reglas = {
    # El admin y la cuenta de backup (scripts/backup_firebase.py) leen la base
    # entera de una vez; "backup" no tiene ninguna regla de escritura.
    ".read": f"auth != null && ({ROL} === 'admin' || {ROL} === 'backup')",
    "users": {
        ".read": ES_ADMIN,
        "$uid": {
            ".read": PROPIO,
            ".write": ES_ADMIN,
            "email": {".write": PROPIO},
            "nombre": {".write": PROPIO},
            "rolSolicitado": {".write": f"{PROPIO} && {SIN_ROL_AUN}"},
            "solicitadoEl": {".write": f"{PROPIO} && {SIN_ROL_AUN}"},
        },
    },
    "rolesConfig": {".read": ES_ADMIN, ".write": ES_ADMIN},
    "temporadasInfo": {".read": TIENE_ROL, ".write": ES_ADMIN},
    "temporadas": {"$t": {"$nodo": POR_CATEGORIA}},
}
for nodo in NODOS_CLUB:
    reglas[nodo] = POR_CATEGORIA

destino = Path(__file__).resolve().parent.parent / "firebase" / "rules.example.json"
destino.write_text(json.dumps({"rules": reglas}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Escrito {destino}")
