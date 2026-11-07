---
name: creacion-fotos
description: Creación y edición de fotos e imágenes para el equipo de marketing, diseño y ventas de Maracuyá. Úsala cuando pidan crear un post, story, banner, flyer de promoción, foto de producto/catálogo, collage, redimensionar para redes, poner logo o marca de agua, retocar/mejorar una foto, quitar fondo, o generar imágenes con IA (Canva).
---

# Creación de fotos — Maracuyá

Script principal: `.claude/skills/creacion-fotos/scripts/fotos.py` (Pillow). Usa la identidad real de **Maracuyá Textil** desde `marca/` (colores, Archivo, logos, WhatsApp, handle). **Lee `marca/README.md` antes de diseñar** y, si existe, el brand book en `marca/brand/`.

Colores por nombre: `gold` #F6CD00, `negro`, `blanco`, `gris-texto`, `gris-etiqueta` (o hex). No hay otras paletas de marca.

**Dos estilos, nunca mezclados en una pieza:**
- `--estilo gold` (Inundada Gold): fondo gold, titular negro en minúsculas con mayúscula inicial, píldora negra con el WhatsApp en gold. Sin grano.
- `--estilo negro` (Editorial oscura): fondo negro con grano, foto real a sangre, titular gigante condensado en gold y mayúsculas. Gold en un solo punto.

```bash
F="python3 .claude/skills/creacion-fotos/scripts/fotos.py"
```

## Comandos

| Necesidad | Comando |
|---|---|
| Post Inundada Gold | `$F post out.png --titulo "Tus redes, en tu espalda." --subtitulo "Bordado en nuestro taller en Caracas." --precio '$14' --nota-precio "c/u por docena" --cinta "100 % algodón / oversize o clásica"` |
| Post Gold con foto (panel) | `$F post out.png --titulo "Así nace tu franela." --foto taller.jpg` |
| Post Editorial oscura | `$F post out.png --estilo negro --titulo "Tu logo, bordado." --foto macro.jpg --precio '$14'` |
| Story / reel-portada | añade `--formato story` (respeta zonas seguras 250/400 px) |
| Cambiar el botón | `--cta "Pídela al"` (por defecto "Escríbenos al" + WhatsApp de la marca); `--cta ""` lo quita |
| Redimensionar a redes | `$F redimensionar foto.jpg carpeta/ --formato post,story,facebook --modo desenfoque` (`todos` = todos los formatos) |
| Logo / marca de agua | `$F logo in.jpg out.jpg --posicion abajo-der --opacidad 0.8` |
| Retoque rápido | `$F mejorar in.jpg out.jpg --calido` |
| Quitar fondo liso | `$F quitar-fondo in.jpg out.png --tolerancia 60` |
| Foto de producto / catálogo | `$F producto prod.png out.jpg --fondo gold --logo` (o `--fondo negro`) |
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

## Copy (tono Maracuyá)
- Español venezolano, tuteo, frases cortas. Habla de lo que gana el cliente: «Tus redes, en tu espalda.», «Tu logo, en el pecho.», «Uniforma a tu equipo.».
- 1 titular + 1 línea de apoyo + 1 dato/CTA. Un solo precio protagonista.
- Nada de «el mejor», «calidad premium», testimonios ni cifras inventadas. Precios reales (pídelos si no los tienes).
- «Delivery gratis a *casi* toda Caracas». Sin emojis en las piezas.
- Ofrece 2–3 variantes de copy cuando sea una campaña.

## Imagen
Solo fotos reales del taller y las prendas (macro del bordado, manos trabajando, prenda puesta, flat lay). Nada de stock, neón, degradados arcoíris ni clip-art. Para una pieza con IA en Canva, que sea utilería o fondo, nunca un producto falso.

## Revisión antes de entregar
Abre siempre la imagen resultante (Read) y pasa el checklist de `marca/README.md`: ¿se entiende en 1 segundo en el celular?, ¿el protagonista es el producto real?, ¿gold sin mezclar estilos?, ¿solo Archivo?, ¿el texto no tapa el bordado?, ¿tildes correctas? Guarda en `entregas/fotos/AAAA-MM-DD_nombre.png` (o donde pida el usuario) y muéstrala con SendUserFile.
