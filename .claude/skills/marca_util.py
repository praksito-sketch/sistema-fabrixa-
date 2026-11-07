"""Utilidades compartidas: carga de la marca Maracuyá y resolución de fuentes."""
import json
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MARCA_PATH = RAIZ / "marca" / "marca.json"


def cargar_marca() -> dict:
    try:
        return json.loads(MARCA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"colores": {"primario": "#5B2A6E", "secundario": "#F6C700",
                            "claro": "#FFF8E7", "oscuro": "#1E1024"},
                "fuentes": {"titulos": "Inter Display:bold", "texto": "Inter"}}


def color(nombre_o_hex: str) -> str:
    """Acepta un nombre de la paleta (primario, secundario...) o un hex."""
    if nombre_o_hex.startswith("#"):
        return nombre_o_hex
    return cargar_marca()["colores"].get(nombre_o_hex, nombre_o_hex)


def fuente(rol_o_patron: str = "titulos") -> str:
    """Devuelve la ruta del archivo de fuente (rol de la marca o patrón fontconfig)."""
    patron = cargar_marca().get("fuentes", {}).get(rol_o_patron, rol_o_patron)
    for cand in (RAIZ / patron, Path(patron)):
        if cand.is_file():
            return str(cand)
    out = subprocess.run(["fc-match", "-f", "%{file}", patron],
                         capture_output=True, text=True)
    return out.stdout.strip() or "DejaVuSans-Bold.ttf"


def logo(variante: str | None = None) -> Path | None:
    m = cargar_marca()
    rel = m.get("logos", {}).get(variante) if variante else None
    ruta = RAIZ / (rel or m.get("logo", "marca/logo.png"))
    return ruta if ruta.is_file() else None
