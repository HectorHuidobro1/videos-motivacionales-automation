# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos esenciales

```powershell
npm start          # Abre el preview interactivo en http://localhost:3000
npm run build      # Renderiza out/video.mp4 (tarda varios minutos)
npm run typecheck  # Verifica tipos TypeScript sin compilar
```

Render de un frame específico para verificar visualmente sin renderizar todo:
```powershell
npx remotion render src/Root.tsx TopPlaces --frames=150 out/test.png
```

## Arquitectura

El entry point es `src/Root.tsx` — registra la composición `TopPlaces` (1080×1920, 30 FPS, 1800 frames = 60 segundos) con `registerRoot()`.

**Flujo de escenas en `src/TopPlaces.tsx`:**

```
Intro (frames 0–150)
  └── 5 × PlaceScene (frames 150–1650, 300 frames cada una)
Outro (frames 1650–1800)
```

El audio `public/music.mp3` corre sobre toda la composición con volumen 0.7.

**`PlaceScene`** es el único componente reutilizable — recibe `{ rank, name, location, fact, imageUrl }` y maneja internamente todas sus animaciones con `useCurrentFrame()`. El timing interno de cada escena:

- Frames 0–30: fade in
- Frames 30–60: número rank sube con `spring()`
- Frames 60–90: nombre fade + slide
- Frames 120–150: ubicación fade
- Frames 180–210: dato curioso fade
- Frames 270–300: fade out

Para agregar o cambiar lugares, editar el array `PLACES` en `src/TopPlaces.tsx`.

## Convenciones de animación

- Usar `interpolate()` con `extrapolateRight: 'clamp'` siempre para evitar valores fuera de rango
- Usar `spring()` para movimientos físicos (rebote), `interpolate()` para fades lineales
- Los frames en `<Sequence from={N}>` son relativos al inicio de esa secuencia — `useCurrentFrame()` dentro del componente hijo empieza en 0

## Requisitos

- Node.js >= 18
- `public/music.mp3` debe existir para el render con audio
- Imágenes via URL de Unsplash: `https://images.unsplash.com/photo-{ID}?w=1080&h=1920&fit=crop&q=80`

## Pipeline de videos motivacionales (voz + subtítulos)

Composiciones adicionales registradas en `src/Root.tsx`: `Motivacional` (`MotivationalVideo.tsx`, subtítulos en frases cortas tipo TikTok), `MotivacionalKaraoke` (`MotivationalVideoKaraoke.tsx`, subtítulos tipo karaoke palabra por palabra, **fondo negro — "formato 1"**) y `MotivacionalBroll` (`MotivationalVideoBroll.tsx`, mismo estilo de subtítulos karaoke pero con un clip de video de Pexels por oración de fondo, **"formato 2"**). Todas leen `public/voice.mp3` como audio y duran lo que dure el audio + 2s de margen. `MotivationalVideoKaraoke.tsx` y `MotivationalVideoBroll.tsx` comparten el componente `KaraokeText` (`src/KaraokeText.tsx`) — no duplicarlo, editar ahí si hay que cambiar tipografía/colores/timing del texto.

**Generar un video nuevo:**

```powershell
python generate.py "Tu guion aqui"          # o: python generate.py --file script.txt
npm run build:motivacional                  # subtítulos en frases cortas (usa src/captions.json)
npm run build:karaoke                       # formato 1: fondo negro (usa src/captions_karaoke.json)

# Para formato 2 (fondo b-roll), además:
python fetch_clips.py                       # descarga clips de Pexels según src/clip_queries.json -> src/clips.json
npm run build:broll                         # formato 2: fondo de video (usa src/captions_karaoke.json + src/clips.json)
```

`generate.py` hace dos cosas: genera la voz con Gemini TTS (`public/voice.mp3`) y transcribe con Groq Whisper para obtener timestamps por palabra. Si ya existe `voice.mp3` y solo hace falta re-generar los subtítulos (por ejemplo tras editarlo a mano), usar `python generate.py --recaption` (frases cortas → `captions.json`) o `python generate.py --karaoke` (oraciones completas → `captions_karaoke.json`) en vez de regenerar el audio.

- **Voz confirmada:** `Algenib` con `PITCH_SHIFT_SEMITONES = -1` (`generate.py:25-26`) — el pitch-shift se aplica automáticamente vía ffmpeg dentro de `generate_tts()`. Se probaron 12 voces nativas de Gemini (Charon, Fenrir, Orus, Gacrux, Rasalgethi, Enceladus, Schedar, Sadaltager, Umbriel, Kore, Alnilam, Algenib) buscando imitar el tono grave/misterioso de un Short de referencia; Algenib fue la más cercana en timbre, y -1 semitono el punto justo (-4 ya sonaba demasiado grave). Gemini TTS no clona voces (catálogo fijo de presets) — si se necesita el timbre exacto de una referencia externa, la única vía es un servicio de voice cloning como ElevenLabs. No volver a preguntar por la voz ni cambiarla salvo pedido explícito.
- Requiere `.env` con `GOOGLE_API_KEY` (Gemini TTS), `GROQ_API_KEY` (Whisper transcripción) y `PEXELS_API_KEY` (clips de fondo, solo formato 2).
- `test_voices.py` genera muestras cortas en `voice_samples/` para comparar voces antes de decidir — usar solo si se quiere reevaluar la voz.
- Los clips de `public/clips/` están gitignoreados (pesan mucho); `src/clip_queries.json` y `src/clips.json` sí se commitean para no perder el mapeo. `fetch_clips.py` re-codifica cada clip a 30fps CFR con GOP corto (`-g 30 -bf 0`, ver el propio script) — necesario para evitar errores intermitentes de render en Windows; no bajar la calidad de ese re-encode sin motivo.

**Al escribir cualquier guion nuevo:** la primera frase debe ser un gancho directamente ligado al tema (afirmación fuerte, pregunta directa, o algo contraintuitivo) para retener al espectador desde el segundo 1 — no una introducción genérica. Y al terminar de renderizar un video, siempre entregar sin que lo pidan: 2-3 opciones de título, descripción con hashtags, y tags de YouTube.
