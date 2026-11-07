#!/usr/bin/env python3
"""Edición de video para Maracuyá (envoltorio de ffmpeg).

Uso: python3 video.py <comando> [opciones]   (ver --help de cada comando)
"""
import argparse
import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from marca_util import color, fuente, logo  # noqa: E402

FORMATOS = {  # ancho x alto
    "reel": (1080, 1920), "story": (1080, 1920), "tiktok": (1080, 1920),
    "feed": (1080, 1350), "cuadrado": (1080, 1080), "youtube": (1920, 1080),
}


def run(cmd):
    print("▶", " ".join(str(c) for c in cmd), file=sys.stderr)
    subprocess.run([str(c) for c in cmd], check=True)


def ff(*args):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args])


def info(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                          "-show_format", "-show_streams", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def tiene_audio(path):
    return any(s["codec_type"] == "audio" for s in info(path)["streams"])


def duracion(path):
    return float(info(path)["format"]["duration"])


def hexff(c):  # "#RRGGBB" -> "0xRRGGBB" para ffmpeg
    return "0x" + color(c).lstrip("#")


def archivo_texto(texto):
    """Guarda el texto en un archivo temporal (evita problemas de escape en drawtext)."""
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write(texto)
    f.close()
    return f.name


SALIDA_VIDEO = ["-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
SALIDA_AUDIO = ["-c:a", "aac", "-b:a", "192k"]


# ---------------------------------------------------------------- comandos
def cmd_info(a):
    d = info(a.entrada)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), {})
    print(json.dumps({
        "duracion_s": round(float(d["format"]["duration"]), 2),
        "resolucion": f'{v.get("width")}x{v.get("height")}',
        "fps": v.get("r_frame_rate"), "codec": v.get("codec_name"),
        "audio": tiene_audio(a.entrada),
        "tamano_mb": round(int(d["format"]["size"]) / 1e6, 2),
    }, indent=2, ensure_ascii=False))


def cmd_cortar(a):
    args = ["-ss", a.inicio, "-i", a.entrada]
    if a.fin:
        args += ["-to", str(float_ts(a.fin) - float_ts(a.inicio))]
    ff(*args, *SALIDA_VIDEO, *SALIDA_AUDIO, a.salida)


def float_ts(t):
    partes = [float(p) for p in str(t).split(":")]
    s = 0.0
    for p in partes:
        s = s * 60 + p
    return s


def cmd_formato(a):
    w, h = FORMATOS[a.formato]
    if a.modo == "recortar":
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1"
    elif a.modo == "barras":
        vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
              f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={hexff(a.color)},setsar=1")
    else:  # desenfoque: el mismo video desenfocado de fondo
        vf = (f"split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,"
              f"crop={w}:{h},boxblur=30:5,eq=brightness=-0.08[fondo];"
              f"[b]scale={w}:{h}:force_original_aspect_ratio=decrease[frente];"
              f"[fondo][frente]overlay=(W-w)/2:(H-h)/2,setsar=1")
    ff("-i", a.entrada, "-filter_complex", vf, "-r", "30",
       *SALIDA_VIDEO, *SALIDA_AUDIO, a.salida)


def cmd_texto(a):
    pos = {"arriba": "h*0.10", "centro": "(h-text_h)/2", "abajo": "h*0.80-text_h"}[a.posicion]
    enable = f":enable='between(t,{a.desde},{a.hasta})'" if a.hasta else ""
    caja = (f":box=1:boxcolor={hexff(a.fondo)}@0.85:boxborderw=28" if a.fondo else
            ":borderw=4:bordercolor=black@0.6")
    v = next(s for s in info(a.entrada)["streams"] if s["codec_type"] == "video")
    w, h = v["width"], v["height"]
    lineas = textwrap.wrap(a.texto, 22 if h > w else 40) or [a.texto]
    # tamaño pedido, reducido si la línea más larga no cabe en el 88% del ancho
    tam = int(min(h * a.tamano, w * 0.88 / (max(map(len, lineas)) * 0.56)))
    vf = (f"drawtext=fontfile='{fuente(a.fuente)}':textfile='{archivo_texto(chr(10).join(lineas))}':"
          f"expansion=none:line_spacing={tam // 4}:fontsize={tam}:fontcolor={hexff(a.color)}:x=(w-text_w)/2:y={pos}{caja}{enable}")
    ff("-i", a.entrada, "-vf", vf, *SALIDA_VIDEO, "-c:a", "copy", a.salida)


def cmd_logo(a):
    ruta = a.logo or logo()
    if not ruta:
        sys.exit("No hay logo: coloca marca/logo.png o pasa --logo")
    m = 40
    xy = {"arriba-izq": f"{m}:{m}", "arriba-der": f"W-w-{m}:{m}",
          "abajo-izq": f"{m}:H-h-{m}", "abajo-der": f"W-w-{m}:H-h-{m}"}[a.posicion]
    fc = (f"[1:v][0:v]scale2ref=w=iw*{a.escala}:h=ow/mdar[lg][v];"
          f"[lg]format=rgba,colorchannelmixer=aa={a.opacidad}[lg2];[v][lg2]overlay={xy}")
    ff("-i", a.entrada, "-i", ruta, "-filter_complex", fc,
       *SALIDA_VIDEO, "-c:a", "copy", a.salida)


def cmd_subtitulos(a):
    c = color(a.color).lstrip("#")
    bgr = c[4:6] + c[2:4] + c[0:2]  # ASS usa &HBBGGRR
    nombre = Path(fuente("titulos")).stem
    estilo = (f"FontName={nombre},Fontsize={a.tamano},PrimaryColour=&H00{bgr},"
              "OutlineColour=&H80000000,BorderStyle=1,Outline=3,Shadow=0,"
              f"Alignment=2,MarginV={a.margen}")
    srt = str(Path(a.srt).resolve()).replace(":", "\\:").replace("'", "\\'")
    ff("-i", a.entrada, "-vf", f"subtitles='{srt}':force_style='{estilo}'",
       *SALIDA_VIDEO, "-c:a", "copy", a.salida)


def cmd_musica(a):
    dur = duracion(a.entrada)
    fade_out = max(dur - 1.5, 0)
    musica = (f"[1:a]volume={a.volumen},afade=t=in:d=1,"
              f"afade=t=out:st={fade_out}:d=1.5[m]")
    if tiene_audio(a.entrada) and not a.reemplazar:
        fc = f"{musica};[0:a][m]amix=inputs=2:duration=first:normalize=0[out]"
    else:
        fc = musica.replace("[m]", "[out]")
    ff("-i", a.entrada, "-stream_loop", "-1", "-i", a.musica, "-filter_complex", fc,
       "-map", "0:v", "-map", "[out]", "-t", str(dur), "-c:v", "copy", *SALIDA_AUDIO, a.salida)


def cmd_unir(a):
    w, h = FORMATOS[a.formato]
    n = len(a.clips)
    entradas, filtros = [], []
    for i, clip in enumerate(a.clips):
        entradas += ["-i", clip]
        filtros.append(f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                       f"crop={w}:{h},setsar=1,fps=30,format=yuv420p[v{i}]")
        if tiene_audio(clip):
            filtros.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        else:
            filtros.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{duracion(clip)}[a{i}]")
    if a.transicion > 0 and n > 1:
        t, offset, prev_v, prev_a = a.transicion, 0.0, "v0", "a0"
        for i in range(1, n):
            offset += duracion(a.clips[i - 1]) - t
            filtros.append(f"[{prev_v}][v{i}]xfade=transition=fade:duration={t}:offset={offset}[xv{i}]")
            filtros.append(f"[{prev_a}][a{i}]acrossfade=d={t}[xa{i}]")
            prev_v, prev_a = f"xv{i}", f"xa{i}"
        mapv, mapa = prev_v, prev_a
    else:
        filtros.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")
        mapv, mapa = "cv", "ca"
    ff(*entradas, "-filter_complex", ";".join(filtros), "-map", f"[{mapv}]",
       "-map", f"[{mapa}]", *SALIDA_VIDEO, *SALIDA_AUDIO, a.salida)


def cmd_fotos(a):
    """Slideshow de fotos con efecto Ken Burns (zoom suave)."""
    w, h = FORMATOS[a.formato]
    fps, frames = 30, int(a.duracion * 30)
    with tempfile.TemporaryDirectory() as tmp:
        clips = []
        for i, foto in enumerate(a.fotos):
            out = Path(tmp) / f"c{i}.mp4"
            zoom = (f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,crop={w*2}:{h*2},"
                    f"zoompan=z='min(zoom+0.0010,1.15)':d={frames}:"
                    f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={fps},setsar=1")
            ff("-loop", "1", "-i", foto, "-vf", zoom, "-t", str(a.duracion), *SALIDA_VIDEO, out)
            clips.append(str(out))
        ns = argparse.Namespace(clips=clips, formato=a.formato, transicion=a.transicion,
                                salida=a.salida)
        if a.musica:
            ns.salida = str(Path(tmp) / "sin_musica.mp4")
            cmd_unir(ns)
            cmd_musica(argparse.Namespace(entrada=ns.salida, musica=a.musica,
                                          volumen=1.0, reemplazar=True, salida=a.salida))
        else:
            cmd_unir(ns)


def cmd_velocidad(a):
    f = a.factor
    atempo, r = [], f
    while r > 2.0:
        atempo.append("atempo=2.0"); r /= 2.0
    while r < 0.5:
        atempo.append("atempo=0.5"); r /= 0.5
    atempo.append(f"atempo={r}")
    args = ["-i", a.entrada, "-vf", f"setpts=PTS/{f}"]
    args += ["-af", ",".join(atempo)] if tiene_audio(a.entrada) else []
    ff(*args, *SALIDA_VIDEO, *SALIDA_AUDIO, a.salida)


def cmd_portada(a):
    ff("-ss", a.segundo, "-i", a.entrada, "-frames:v", "1", "-q:v", "2", a.salida)


def cmd_gif(a):
    fc = (f"fps={a.fps},scale={a.ancho}:-1:flags=lanczos,split[s0][s1];"
          "[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer")
    args = ["-ss", a.inicio] + (["-t", a.duracion] if a.duracion else [])
    ff(*args, "-i", a.entrada, "-filter_complex", fc, a.salida)


def cmd_comprimir(a):
    dur = duracion(a.entrada)
    kbps = int(a.mb * 8000 / dur) - 128
    if kbps < 200:
        sys.exit(f"{a.mb} MB es muy poco para {dur:.0f}s de video")
    with tempfile.TemporaryDirectory() as tmp:
        log = str(Path(tmp) / "pass")
        comun = ["-i", a.entrada, "-c:v", "libx264", "-b:v", f"{kbps}k", "-pix_fmt", "yuv420p",
                 "-passlogfile", log]
        ff(*comun, "-pass", "1", "-an", "-f", "mp4", "/dev/null")
        ff(*comun, "-pass", "2", *SALIDA_AUDIO[:2], "-b:a", "128k", "-movflags", "+faststart", a.salida)


def cmd_color(a):
    """Corrección rápida: brillo, contraste, saturación + look de marca opcional."""
    vf = f"eq=brightness={a.brillo}:contrast={a.contraste}:saturation={a.saturacion}"
    if a.calido:
        vf += ",colorbalance=rs=0.06:gs=0.02:bs=-0.06"
    if a.vineta:
        vf += ",vignette=PI/5"
    ff("-i", a.entrada, "-vf", vf, *SALIDA_VIDEO, "-c:a", "copy", a.salida)


def cmd_audio(a):
    """Normaliza el volumen de la voz (-14 LUFS, estándar redes) y quita ruido leve."""
    af = "highpass=f=80,afftdn=nf=-25," if a.limpiar else ""
    af += "loudnorm=I=-14:TP=-1.5:LRA=11"
    ff("-i", a.entrada, "-af", af, "-c:v", "copy", *SALIDA_AUDIO, a.salida)


# ---------------------------------------------------------------- CLI
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    def sub(nombre, fn, ayuda, entrada=True, salida=True):
        s = sp.add_parser(nombre, help=ayuda)
        if entrada:
            s.add_argument("entrada")
        if salida:
            s.add_argument("salida")
        s.set_defaults(fn=fn)
        return s

    sub("info", cmd_info, "datos técnicos del video", salida=False)

    s = sub("cortar", cmd_cortar, "recortar un tramo (tiempos en s o mm:ss)")
    s.add_argument("--inicio", default="0"); s.add_argument("--fin")

    s = sub("formato", cmd_formato, "adaptar a reel/story/feed/cuadrado/youtube")
    s.add_argument("--formato", choices=FORMATOS, default="reel")
    s.add_argument("--modo", choices=["desenfoque", "recortar", "barras"], default="desenfoque")
    s.add_argument("--color", default="primario", help="color de barras")

    s = sub("texto", cmd_texto, "texto/título sobre el video")
    s.add_argument("--texto", required=True)
    s.add_argument("--posicion", choices=["arriba", "centro", "abajo"], default="arriba")
    s.add_argument("--tamano", type=float, default=0.045, help="fracción de la altura")
    s.add_argument("--color", default="claro"); s.add_argument("--fondo", help="color de caja")
    s.add_argument("--fuente", default="titulos")
    s.add_argument("--desde", default="0"); s.add_argument("--hasta")

    s = sub("logo", cmd_logo, "marca de agua con el logo")
    s.add_argument("--logo"); s.add_argument("--escala", type=float, default=0.18)
    s.add_argument("--opacidad", type=float, default=0.9)
    s.add_argument("--posicion", choices=["arriba-izq", "arriba-der", "abajo-izq", "abajo-der"],
                   default="abajo-der")

    s = sub("subtitulos", cmd_subtitulos, "quemar subtítulos .srt con estilo de marca")
    s.add_argument("--srt", required=True); s.add_argument("--tamano", type=int, default=14)
    s.add_argument("--color", default="secundario"); s.add_argument("--margen", type=int, default=60)

    s = sub("musica", cmd_musica, "añadir música de fondo (loop + fades)")
    s.add_argument("--musica", required=True); s.add_argument("--volumen", type=float, default=0.25)
    s.add_argument("--reemplazar", action="store_true", help="quitar audio original")

    s = sub("unir", cmd_unir, "unir varios clips", entrada=False, salida=False)
    s.add_argument("clips", nargs="+"); s.add_argument("-o", "--salida", required=True)
    s.add_argument("--formato", choices=FORMATOS, default="reel")
    s.add_argument("--transicion", type=float, default=0.0, help="segundos de fundido")

    s = sub("fotos", cmd_fotos, "video slideshow desde fotos", entrada=False, salida=False)
    s.add_argument("fotos", nargs="+"); s.add_argument("-o", "--salida", required=True)
    s.add_argument("--formato", choices=FORMATOS, default="reel")
    s.add_argument("--duracion", type=float, default=3.0, help="segundos por foto")
    s.add_argument("--transicion", type=float, default=0.5); s.add_argument("--musica")

    s = sub("velocidad", cmd_velocidad, "acelerar/ralentizar (factor 2 = doble)")
    s.add_argument("--factor", type=float, required=True)

    s = sub("portada", cmd_portada, "extraer un fotograma como miniatura")
    s.add_argument("--segundo", default="1")

    s = sub("gif", cmd_gif, "convertir tramo a GIF")
    s.add_argument("--inicio", default="0"); s.add_argument("--duracion")
    s.add_argument("--fps", type=int, default=12); s.add_argument("--ancho", type=int, default=480)

    s = sub("comprimir", cmd_comprimir, "comprimir a un tamaño objetivo (WhatsApp, email)")
    s.add_argument("--mb", type=float, default=15)

    s = sub("color", cmd_color, "corrección de color rápida")
    s.add_argument("--brillo", type=float, default=0.03)
    s.add_argument("--contraste", type=float, default=1.08)
    s.add_argument("--saturacion", type=float, default=1.15)
    s.add_argument("--calido", action="store_true"); s.add_argument("--vineta", action="store_true")

    s = sub("audio", cmd_audio, "normalizar volumen para redes (-14 LUFS)")
    s.add_argument("--limpiar", action="store_true", help="reducir ruido de fondo")

    a = p.parse_args()
    a.fn(a)
    if getattr(a, "salida", None):
        print(f"✔ {a.salida}")


if __name__ == "__main__":
    main()
