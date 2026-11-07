#!/usr/bin/env python3
"""Creación y edición de fotos para Maracuyá (Pillow).

Uso: python3 fotos.py <comando> [opciones]   (ver --help de cada comando)
"""
import argparse
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from marca_util import cargar_marca, color, fuente, logo  # noqa: E402

FORMATOS = {
    "post": (1080, 1350), "cuadrado": (1080, 1080), "story": (1080, 1920),
    "reel-portada": (1080, 1920), "facebook": (1200, 630), "portada-fb": (1640, 624),
    "linkedin": (1200, 627), "youtube-mini": (1280, 720), "whatsapp": (800, 800),
    "catalogo": (2000, 2000), "banner-web": (1920, 600),
}


def abrir(ruta):
    return ImageOps.exif_transpose(Image.open(ruta)).convert("RGBA")


def guardar(img, salida):
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    if salida.suffix.lower() in (".jpg", ".jpeg"):
        img.convert("RGB").save(salida, quality=92, optimize=True, progressive=True)
    elif salida.suffix.lower() == ".webp":
        img.save(salida, quality=88)
    else:
        img.save(salida, optimize=True)
    print(f"✔ {salida}")


def rgb(c):
    return color(c)


def ajustar(img, w, h, modo="recortar", fondo="claro"):
    if modo == "recortar":
        return ImageOps.fit(img, (w, h), Image.LANCZOS)
    lienzo = Image.new("RGBA", (w, h), rgb(fondo))
    if modo == "desenfoque":
        lienzo = ImageOps.fit(img, (w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
        lienzo = ImageEnhance.Brightness(lienzo).enhance(0.85)
    copia = img.copy()
    copia.thumbnail((w, h), Image.LANCZOS)
    lienzo.alpha_composite(copia, ((w - copia.width) // 2, (h - copia.height) // 2))
    return lienzo


def pegar_logo(img, ruta=None, escala=0.18, posicion="abajo-der", opacidad=0.9):
    ruta = ruta or logo()
    if not ruta:
        print("⚠ sin logo (coloca marca/logo.png)", file=sys.stderr)
        return img
    lg = Image.open(ruta).convert("RGBA")
    ancho = int(img.width * escala)
    lg = lg.resize((ancho, int(lg.height * ancho / lg.width)), Image.LANCZOS)
    if opacidad < 1:
        alfa = lg.getchannel("A").point(lambda p: int(p * opacidad))
        lg.putalpha(alfa)
    m = int(img.width * 0.04)
    x = m if "izq" in posicion else img.width - lg.width - m
    y = m if "arriba" in posicion else img.height - lg.height - m
    img.alpha_composite(lg, (x, y))
    return img


def texto_ajustado(draw, txt, fnt_path, max_w, tam):
    """Reduce el tamaño hasta que el texto (con saltos de línea) quepa en max_w."""
    while tam > 12:
        f = ImageFont.truetype(fnt_path, tam)
        chars = max(8, int(max_w / (tam * 0.55)))
        lineas = textwrap.wrap(txt, chars)
        if all(draw.textlength(l, font=f) <= max_w for l in lineas):
            return f, "\n".join(lineas)
        tam -= 4
    return ImageFont.truetype(fnt_path, tam), txt


# ---------------------------------------------------------------- comandos
def cmd_redimensionar(a):
    img = abrir(a.entrada)
    formatos = list(FORMATOS) if a.formato == "todos" else a.formato.split(",")
    base = Path(a.salida)
    for f in formatos:
        w, h = FORMATOS[f]
        out = ajustar(img, w, h, a.modo, a.fondo)
        destino = base if len(formatos) == 1 and base.suffix else base / f"{Path(a.entrada).stem}_{f}.jpg"
        guardar(out, destino)


def cmd_logo(a):
    guardar(pegar_logo(abrir(a.entrada), a.logo, a.escala, a.posicion, a.opacidad), a.salida)


def cmd_mejorar(a):
    img = abrir(a.entrada)
    alfa = img.getchannel("A")
    img = ImageOps.autocontrast(img.convert("RGB"), cutoff=0.5)
    img = ImageEnhance.Brightness(img).enhance(a.brillo)
    img = ImageEnhance.Contrast(img).enhance(a.contraste)
    img = ImageEnhance.Color(img).enhance(a.saturacion)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=a.nitidez, threshold=3))
    if a.calido:
        r, g, b = img.split()
        img = Image.merge("RGB", (r.point(lambda p: min(255, p * 1.05)), g,
                                  b.point(lambda p: p * 0.94)))
    img = img.convert("RGBA"); img.putalpha(alfa)
    guardar(img, a.salida)


def cmd_post(a):
    """Pieza para redes: foto de fondo (o color) + titular + subtítulo + CTA + logo."""
    w, h = FORMATOS[a.formato]
    if a.foto:
        img = ajustar(abrir(a.foto), w, h, "recortar")
        capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        oscuro = Image.new("RGBA", (1, 1), rgb("oscuro")).getpixel((0, 0))[:3]
        for y in range(h):  # degradado inferior para legibilidad
            t = max(0, (y - h * 0.35) / (h * 0.65))
            dc.line([(0, y), (w, y)], fill=(*oscuro, int(220 * t)))
        img.alpha_composite(capa)
    else:
        img = Image.new("RGBA", (w, h), rgb(a.fondo))
    d = ImageDraw.Draw(img)
    m = int(w * 0.08)
    y = h - m
    if a.cta:  # botón CTA
        f = ImageFont.truetype(fuente("titulos"), int(w * 0.04))
        tw = d.textlength(a.cta, font=f)
        bh = int(w * 0.085)
        d.rounded_rectangle([m, y - bh, m + tw + bh, y], radius=bh // 2, fill=rgb("secundario"))
        d.text((m + bh / 2, y - bh / 2), a.cta, font=f, fill=rgb("oscuro"), anchor="lm")
        y -= bh + int(w * 0.05)
    if a.subtitulo:
        f, t = texto_ajustado(d, a.subtitulo, fuente("texto"), w - 2 * m, int(w * 0.042))
        d.multiline_text((m, y), t, font=f, fill=rgb("claro"), anchor="ld", spacing=10)
        y -= d.multiline_textbbox((0, 0), t, font=f, spacing=10)[3] + int(w * 0.03)
    f, t = texto_ajustado(d, a.titulo, fuente("titulos"), w - 2 * m, int(w * 0.095))
    d.multiline_text((m, y), t, font=f, fill=rgb(a.color_titulo), anchor="ld", spacing=8)
    if a.precio:
        f = ImageFont.truetype(fuente("titulos"), int(w * 0.06))
        r = int(w * 0.13)
        cx, cy = w - m - r, m + r
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb("secundario"))
        d.text((cx, cy), a.precio, font=f, fill=rgb("oscuro"), anchor="mm")
    img = pegar_logo(img, posicion="arriba-izq", escala=0.2)
    guardar(img, a.salida)


def cmd_collage(a):
    w, h = FORMATOS[a.formato]
    n = len(a.fotos)
    cols = a.columnas or (1 if n == 1 else 2 if n <= 4 else 3)
    filas = -(-n // cols)
    g = a.espacio
    lienzo = Image.new("RGBA", (w, h), rgb(a.fondo))
    cw, ch = (w - g * (cols + 1)) // cols, (h - g * (filas + 1)) // filas
    for i, ruta in enumerate(a.fotos):
        c, r = i % cols, i // cols
        celda = ImageOps.fit(abrir(ruta), (cw, ch), Image.LANCZOS)
        lienzo.alpha_composite(celda, (g + c * (cw + g), g + r * (ch + g)))
    guardar(pegar_logo(lienzo) if a.logo else lienzo, a.salida)


def cmd_producto(a):
    """Foto de producto (idealmente PNG sin fondo) sobre fondo de marca con sombra."""
    w, h = FORMATOS[a.formato]
    prod = abrir(a.entrada)
    bbox = prod.getchannel("A").getbbox()
    if bbox:
        prod = prod.crop(bbox)
    prod.thumbnail((int(w * a.escala), int(h * a.escala)), Image.LANCZOS)
    if a.degradado:
        arriba = Image.new("RGBA", (w, h), rgb(a.fondo))
        abajo = Image.new("RGBA", (w, h), rgb(a.degradado))
        masc = Image.linear_gradient("L").resize((w, h))
        lienzo = Image.composite(abajo, arriba, masc)
    else:
        lienzo = Image.new("RGBA", (w, h), rgb(a.fondo))
    x, y = (w - prod.width) // 2, (h - prod.height) // 2
    sombra = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse(
        [x + prod.width * 0.1, y + prod.height * 0.95, x + prod.width * 0.9, y + prod.height * 1.05],
        fill=(0, 0, 0, 90))
    lienzo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(25)))
    lienzo.alpha_composite(prod, (x, y))
    guardar(pegar_logo(lienzo) if a.logo else lienzo, a.salida)


def cmd_quitar_fondo(a):
    """Quita fondos lisos (blanco/de estudio) por tolerancia de color.
    Para fondos complejos usar Canva (remove-background) o rembg."""
    img = abrir(a.entrada)
    base = img.convert("RGB")
    ref = Image.new("RGB", base.size, base.getpixel((2, 2)))
    r, g, b = ImageChops.difference(base, ref).split()
    dif = ImageChops.add(ImageChops.add(r, g), b)  # suma de diferencias por canal
    fondo = dif.point(lambda p: 0 if p < a.tolerancia else 255)
    alfa = ImageChops.multiply(img.getchannel("A"), fondo).filter(ImageFilter.MedianFilter(3))
    img.putalpha(alfa)
    guardar(img, a.salida if a.salida.lower().endswith(".png") else a.salida + ".png")


def cmd_paleta(a):
    """Muestra la paleta de marca como imagen (para validar colores)."""
    cols = cargar_marca()["colores"]
    w = 220
    img = Image.new("RGBA", (w * len(cols), 300), "white")
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(fuente("texto"), 22)
    for i, (n, hx) in enumerate(cols.items()):
        d.rectangle([i * w, 0, (i + 1) * w, 220], fill=hx)
        d.text((i * w + 12, 235), f"{n}\n{hx}", font=f, fill="black")
    guardar(img, a.salida)


# ---------------------------------------------------------------- CLI
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    todos = ", ".join(FORMATOS)

    s = sp.add_parser("redimensionar", help="adaptar foto a formatos de redes")
    s.add_argument("entrada"); s.add_argument("salida", help="archivo o carpeta")
    s.add_argument("--formato", default="post", help=f"uno, varios (a,b) o 'todos': {todos}")
    s.add_argument("--modo", choices=["recortar", "encajar", "desenfoque"], default="recortar")
    s.add_argument("--fondo", default="claro"); s.set_defaults(fn=cmd_redimensionar)

    s = sp.add_parser("logo", help="marca de agua con logo")
    s.add_argument("entrada"); s.add_argument("salida"); s.add_argument("--logo")
    s.add_argument("--escala", type=float, default=0.18); s.add_argument("--opacidad", type=float, default=0.9)
    s.add_argument("--posicion", default="abajo-der",
                   choices=["arriba-izq", "arriba-der", "abajo-izq", "abajo-der"])
    s.set_defaults(fn=cmd_logo)

    s = sp.add_parser("mejorar", help="retoque automático (luz, color, nitidez)")
    s.add_argument("entrada"); s.add_argument("salida")
    s.add_argument("--brillo", type=float, default=1.04); s.add_argument("--contraste", type=float, default=1.08)
    s.add_argument("--saturacion", type=float, default=1.15); s.add_argument("--nitidez", type=int, default=80)
    s.add_argument("--calido", action="store_true"); s.set_defaults(fn=cmd_mejorar)

    s = sp.add_parser("post", help="pieza de redes con titular, CTA, precio y logo")
    s.add_argument("salida"); s.add_argument("--titulo", required=True)
    s.add_argument("--subtitulo"); s.add_argument("--cta"); s.add_argument("--precio")
    s.add_argument("--foto"); s.add_argument("--fondo", default="primario")
    s.add_argument("--color-titulo", default="secundario")
    s.add_argument("--formato", choices=FORMATOS, default="post"); s.set_defaults(fn=cmd_post)

    s = sp.add_parser("collage", help="cuadrícula de fotos")
    s.add_argument("fotos", nargs="+"); s.add_argument("-o", "--salida", required=True)
    s.add_argument("--formato", choices=FORMATOS, default="cuadrado")
    s.add_argument("--columnas", type=int); s.add_argument("--espacio", type=int, default=16)
    s.add_argument("--fondo", default="claro"); s.add_argument("--logo", action="store_true")
    s.set_defaults(fn=cmd_collage)

    s = sp.add_parser("producto", help="producto sobre fondo de marca con sombra")
    s.add_argument("entrada"); s.add_argument("salida")
    s.add_argument("--formato", choices=FORMATOS, default="catalogo")
    s.add_argument("--fondo", default="claro"); s.add_argument("--degradado", help="color inferior")
    s.add_argument("--escala", type=float, default=0.7); s.add_argument("--logo", action="store_true")
    s.set_defaults(fn=cmd_producto)

    s = sp.add_parser("quitar-fondo", help="quitar fondo liso (blanco/estudio)")
    s.add_argument("entrada"); s.add_argument("salida")
    s.add_argument("--tolerancia", type=int, default=60); s.set_defaults(fn=cmd_quitar_fondo)

    s = sp.add_parser("paleta", help="imagen con la paleta de marca")
    s.add_argument("salida"); s.set_defaults(fn=cmd_paleta)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
