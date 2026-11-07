---
name: edicion-video
description: Edición de video para el equipo de marketing, diseño y ventas de Maracuyá. Úsala cuando pidan editar, cortar, recortar, unir clips, hacer un reel/TikTok/story, adaptar formato (9:16, 4:5, 1:1, 16:9), poner texto, subtítulos, logo o música, crear un video con fotos (slideshow), acelerar, sacar miniatura/portada, GIF, comprimir para WhatsApp, corregir color o normalizar audio. También para generar videos con IA vía Canva.
---

# Edición de video — Maracuyá

Script principal: `.claude/skills/edicion-video/scripts/video.py` (ffmpeg). Usa la identidad de **Maracuyá Textil** en `marca/` (lee `marca/README.md`): colores `gold` #F6CD00 / `negro` / `blanco`, tipografía Archivo y el sticker del logo como marca de agua.

Reglas de video de la marca: textos de reel de 2 a 5 palabras, **en minúsculas, blancos con contorno**; nada importante en los primeros 250 px ni en los últimos 400 px; contenido real del taller (bordado, máquina, manos, prenda puesta); sin transiciones exageradas ni efectos neón.

```bash
V="python3 .claude/skills/edicion-video/scripts/video.py"
```

## Comandos

| Necesidad | Comando |
|---|---|
| Ver duración/resolución | `$V info entrada.mp4` |
| Cortar un tramo | `$V cortar in.mp4 out.mp4 --inicio 0:05 --fin 0:20` |
| Pasar a Reel/TikTok/Story 9:16 | `$V formato in.mp4 out.mp4 --formato reel` (modo `desenfoque` por defecto; `recortar` o `barras --color negro`) |
| Feed 4:5 / cuadrado / YouTube | `--formato feed` / `cuadrado` / `youtube` |
| Titular o gancho | `$V texto in.mp4 out.mp4 --texto "así nace tu franela" --posicion arriba --hasta 3` (con caja: `--fondo gold --color negro`) |
| Logo / marca de agua | `$V logo in.mp4 out.mp4 --posicion abajo-der --escala 0.18` |
| Subtítulos quemados | `$V subtitulos in.mp4 out.mp4 --srt subs.srt` (Archivo Black, blanco con contorno; `--color gold` para resaltar) |
| Música de fondo | `$V musica in.mp4 out.mp4 --musica pista.mp3 --volumen 0.25` (`--reemplazar` quita el audio original) |
| Unir clips | `$V unir c1.mp4 c2.mp4 c3.mp4 -o out.mp4 --formato reel --transicion 0.4` |
| Video desde fotos | `$V fotos f1.jpg f2.jpg f3.jpg -o out.mp4 --duracion 2.5 --musica pista.mp3` |
| Acelerar / cámara lenta | `$V velocidad in.mp4 out.mp4 --factor 2` (0.5 = lento) |
| Miniatura/portada | `$V portada in.mp4 portada.jpg --segundo 3` |
| GIF | `$V gif in.mp4 out.gif --inicio 2 --duracion 3` |
| Comprimir (WhatsApp 16 MB) | `$V comprimir in.mp4 out.mp4 --mb 15` |
| Color más vivo/cálido | `$V color in.mp4 out.mp4 --calido --vineta` |
| Voz más clara y volumen estándar | `$V audio in.mp4 out.mp4 --limpiar` |

Para algo que no cubra el script, usar `ffmpeg` directamente con los mismos ajustes de salida (`libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart`, AAC 192k).

## Flujo recomendado para un Reel de ventas

1. `info` del material → 2. `cortar` lo mejor (gancho en los primeros 2 s) → 3. `unir` con `--formato reel` → 4. `color` → 5. `texto` con el gancho arriba (0–3 s) → 6. `subtitulos` si hay voz (el 80 % lo ve sin sonido) → 7. `musica` → 8. `logo` → 9. `portada`.
Encadena en archivos intermedios (`paso1.mp4`, `paso2.mp4`…) y entrega solo el final.

## Subtítulos
Si hay voz y no hay .srt, transcribe el audio (pide el guion al equipo si no hay herramienta de transcripción) y escribe el .srt con frases de máx. ~32 caracteres por línea y 1–3 s cada una.

## Videos con IA (Canva)
Si el usuario quiere un video generado desde cero o animado con plantillas, usa las herramientas `mcp__Canva__*` (cargarlas con ToolSearch): primero `get-video-production-guide`, luego `create-video` / `get-video-generation-status`, y `export-design` para descargar. Luego se puede post-procesar con este script (logo, música, formato).

## Buenas prácticas por red
- Reels/TikTok: 1080×1920, 7–30 s, texto dentro de la zona segura (evitar 250 px de arriba y 400 px de abajo).
- Feed IG: 1080×1350. YouTube: 1920×1080. WhatsApp: < 16 MB.
- Tono de copy según `marca/marca.json` (`tono`, `ejemplos_copy`). Cierre con WhatsApp 0414-1185571 / @maracuya.textil.

## Entrega
Guarda los resultados en `entregas/video/AAAA-MM-DD_nombre.mp4` dentro del repo (o donde pida el usuario) y muéstralos con SendUserFile. Revisa siempre un fotograma (`portada`) antes de entregar para validar texto y encuadre.
