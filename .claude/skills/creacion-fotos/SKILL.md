---
name: creacion-fotos
description: Creación y edición de fotos e imágenes para el equipo de marketing, diseño y ventas de Maracuyá. Úsala cuando pidan crear un post, story, banner, flyer de promoción, foto de producto/catálogo, collage, redimensionar para redes, poner logo o marca de agua, retocar/mejorar una foto, quitar fondo, o generar imágenes con IA (Canva).
---

# Creación de fotos — Maracuyá

Script principal: `.claude/skills/creacion-fotos/scripts/fotos.py` (Pillow). Usa colores, fuentes y logo de `marca/marca.json` / `marca/logo.png`. Colores por nombre (`primario`, `secundario`, `acento`, `claro`, `oscuro`) o hex.

```bash
F="python3 .claude/skills/creacion-fotos/scripts/fotos.py"
```

## Comandos

| Necesidad | Comando |
|---|---|
| Post de promo con foto | `$F post out.png --foto foto.jpg --titulo "Jugo de maracuyá" --subtitulo "Recién hecho" --cta "Pide por DM" --precio '$9.900'` |
| Post solo color (anuncio) | `$F post out.png --titulo "¡Promo de fin de semana!" --cta "Escríbenos" --fondo primario` |
| Story | añade `--formato story` |
| Redimensionar a redes | `$F redimensionar foto.jpg carpeta/ --formato post,story,facebook --modo desenfoque` (`todos` = todos los formatos) |
| Logo / marca de agua | `$F logo in.jpg out.jpg --posicion abajo-der --opacidad 0.8` |
| Retoque rápido | `$F mejorar in.jpg out.jpg --calido` |
| Quitar fondo liso | `$F quitar-fondo in.jpg out.png --tolerancia 60` |
| Foto de producto / catálogo | `$F producto prod.png out.jpg --fondo claro --degradado secundario --logo` |
| Collage | `$F collage a.jpg b.jpg c.jpg d.jpg -o out.jpg --formato cuadrado --logo` |
| Ver la paleta de marca | `$F paleta paleta.png` |

Formatos: `post` 1080×1350, `cuadrado` 1080×1080, `story`/`reel-portada` 1080×1920, `facebook` 1200×630, `portada-fb` 1640×624, `linkedin` 1200×627, `youtube-mini` 1280×720, `whatsapp` 800×800, `catalogo` 2000×2000, `banner-web` 1920×600.

## Cuándo usar Canva en lugar del script
Carga las herramientas con ToolSearch (`mcp__Canva__...`):
- **Imagen nueva con IA** (no hay foto): `generate-image` → `get-generate-image-job`.
- **Quitar fondo complejo** (personas, pelo, fondos con detalle): `remove-background`.
- **Diseños elaborados / plantillas de marca**: `list-brand-kits`, `search-brand-templates`, `create-design-from-brand-template`, `generate-design`; adaptar tamaños con `resize-design`; descargar con `export-design`.
- Subir fotos locales a Canva: `create-upload-url` o `upload-asset-from-url`.
Para piezas simples y repetitivas (variantes de precio, redimensionar lotes, logo en 50 fotos) el script es más rápido.

## Copy
Escribe titulares cortos (máx. 6–7 palabras), un beneficio en el subtítulo y un CTA claro. Sigue el `tono` y `cta_default` de `marca/marca.json`. Ofrece 2–3 variantes de copy cuando sea una campaña.

## Revisión antes de entregar
Abre siempre la imagen resultante (Read) para comprobar legibilidad, que el texto no tape el producto y que el logo se vea. Guarda en `entregas/fotos/AAAA-MM-DD_nombre.png` (o donde pida el usuario) y muéstrala con SendUserFile.
