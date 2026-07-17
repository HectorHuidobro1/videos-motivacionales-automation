# Video motivacional con fondo b-roll (Pexels) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar una segunda variante de video motivacional (`MotivacionalBroll`) que usa clips de video de stock de Pexels como fondo por cada oración, en vez del fondo negro sólido de `MotivacionalKaraoke`.

**Architecture:** Un script Python (`fetch_clips.py`) descarga un clip de Pexels por cada oración de `src/captions_karaoke.json` (ya generado) según una lista de términos de búsqueda (`src/clip_queries.json`), guardando el mapeo en `src/clips.json`. Una nueva composición Remotion (`MotivationalVideoBroll.tsx`) renderiza un `<Sequence>` por oración con el clip correspondiente de fondo (mudo, en loop), un velo oscuro encima, y el mismo texto karaoke palabra-por-palabra ya existente.

**Tech Stack:** Python 3 (requests, python-dotenv), Remotion 4.x / React / TypeScript, API de Pexels Videos.

## Global Constraints

- Resolución 1080×1920, 30 FPS (spec: formato vertical existente del proyecto).
- Voz: `Algenib` con `PITCH_SHIFT_SEMITONES = -1` (ya configurado en `generate.py`, no modificar).
- Overlay oscuro sobre video: `rgba(0,0,0,0.45)` (spec: mismo nivel que `PlaceScene`).
- Clips de fondo: mudos (`muted`) y en loop (`loop`) — la única pista de audio es `public/voice.mp3`.
- `PEXELS_API_KEY` ya está en `.env` (no requiere acción).
- No modificar `MotivationalVideoKaraoke.tsx` ni la composición `MotivacionalKaraoke` existente — esta es una variante adicional, no un reemplazo.

---

### Task 1: Generar voz y subtítulos del guion nuevo (ya completado)

**Files:**
- Modifica (ya hecho): `public/voice.mp3`, `src/captions.json`, `src/captions_karaoke.json`

**Interfaces:**
- Produce: `src/captions_karaoke.json` con 10 oraciones (array de `{start, end, words: [{word, start, end}]}`), usado por Task 2 y Task 3.

Este paso ya se ejecutó como parte del diseño (para poder mapear términos de búsqueda a oraciones reales sin placeholders). El guion usado:

```
El miedo es un músculo. Si no lo usas, se debilita. Pero si dejas de
enfrentarlo, se vuelve más y más grande, hasta que tu mundo se hace pequeño.

Los niños sobreprotegidos tienen miedo todo el tiempo. Los que se atrevieron
a caerse, a fallar en público, ya no le temen a esas cosas. Porque una
creencia es un pobre sustituto de una experiencia.

La confianza no nace de pensar que puedes. Nace de hacerlo. De tirar mil
veces antes de descansar. De equivocarte y seguir intentando.

Así que deja de esperar sentirte listo. Encara lo que te da miedo. Ahí,
exactamente ahí, es donde se construye quien serás.
```

Las 10 oraciones resultantes en `src/captions_karaoke.json` (índice → texto → tiempo):

| # | Texto | start | end |
|---|---|---|---|
| 0 | El miedo es un músculo. | 0.26 | 2.16 |
| 1 | Si no lo usas, se debilita. | 3.2 | 5.4 |
| 2 | Pero si dejas de enfrentarlo, se vuelve más y más grande. | 6.42 | 11.82 |
| 3 | Hasta que tu mundo se hace pequeño. | 12.92 | 15.28 |
| 4 | Los niños sobreprotegidos tienen miedo todo el tiempo. | 16.94 | 21.4 |
| 5 | Los que se atrevieron a caerse, a fallar en público, ya no le temen a esas cosas. | 21.98 | 28.24 |
| 6 | porque una creencia es un pobre sustituto de una experiencia. | 29.26 | 33.98 |
| 7 | La confianza no nace de pensar que puedes, nace de hacerlo, de tirar mil veces antes de descansar, de equivocarte y seguir intentando. | 35.58 | 48.5 |
| 8 | Así que deja de esperar sentirte listo, encara lo que te da miedo. | 50.08 | 55.06 |
| 9 | Ahí, exactamente ahí, es donde se construye quién serás. | 56.12 | 61.64 |

- [x] **Paso 1:** Guion escrito y guardado.
- [x] **Paso 2:** `python generate.py --file <script>` ejecutado → `public/voice.mp3` generado con voz Algenib -1 semitono.
- [x] **Paso 3:** `python generate.py --karaoke` ejecutado → `src/captions_karaoke.json` con las 10 oraciones de la tabla de arriba.
- [x] **Paso 4:** Verificado leyendo `src/captions_karaoke.json` — 10 oraciones, acentos correctos (UTF-8).

Nada que hacer en este task al ejecutar el plan — es contexto para los tasks siguientes.

---

### Task 2: `fetch_clips.py` — descargar clips de Pexels

**Files:**
- Create: `fetch_clips.py`
- Create: `test_fetch_clips.py`
- Create: `src/clip_queries.json`

**Interfaces:**
- Consumes: `src/captions_karaoke.json` (de Task 1, solo se usa para saber cuántas oraciones hay — 10).
- Produces: `pick_best_video(data: dict) -> str | None` (usado internamente y testeado), `public/clips/clip_0.mp4` ... `clip_9.mp4`, `src/clips.json` = `[{"file": "clip_0.mp4"}, ...]` (consumido por Task 3).

- [ ] **Paso 1: Escribir el test que falla**

Crear `test_fetch_clips.py`:

```python
from fetch_clips import pick_best_video


def test_prefers_portrait():
    data = {
        "videos": [
            {"video_files": [
                {"file_type": "video/mp4", "width": 1920, "height": 1080, "link": "https://landscape.mp4"},
                {"file_type": "video/mp4", "width": 1080, "height": 1920, "link": "https://portrait.mp4"},
            ]}
        ]
    }
    assert pick_best_video(data) == "https://portrait.mp4"


def test_falls_back_to_largest_landscape():
    data = {
        "videos": [
            {"video_files": [
                {"file_type": "video/mp4", "width": 640, "height": 360, "link": "https://small.mp4"},
                {"file_type": "video/mp4", "width": 1920, "height": 1080, "link": "https://big.mp4"},
            ]}
        ]
    }
    assert pick_best_video(data) == "https://big.mp4"


def test_returns_none_for_no_videos():
    assert pick_best_video({"videos": []}) is None


if __name__ == "__main__":
    test_prefers_portrait()
    test_falls_back_to_largest_landscape()
    test_returns_none_for_no_videos()
    print("Todos los tests pasaron.")
```

- [ ] **Paso 2: Correr el test para verificar que falla**

Run: `python test_fetch_clips.py`
Expected: `ModuleNotFoundError: No module named 'fetch_clips'` (todavía no existe el archivo).

- [ ] **Paso 3: Crear `fetch_clips.py` con la implementación mínima**

```python
#!/usr/bin/env python3
"""
fetch_clips.py — Descarga clips de video de Pexels para usar como fondo
en la composicion MotivacionalBroll, uno por cada oracion de captions_karaoke.json.
Uso: python fetch_clips.py
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PROJECT_DIR = Path(__file__).parent
PUBLIC_DIR = PROJECT_DIR / "public"
SRC_DIR = PROJECT_DIR / "src"
CLIPS_DIR = PUBLIC_DIR / "clips"

FALLBACK_QUERIES = [
    "motivation silhouette sunset",
    "person walking determined slow motion",
    "dramatic clouds timelapse",
]


def pick_best_video(data: dict):
    """Elige el mejor archivo de video de una respuesta de Pexels: prefiere
    orientacion portrait (vertical), y si no hay, el de mayor resolucion."""
    all_files = []
    for video in data.get("videos", []):
        for f in video.get("video_files", []):
            if f.get("file_type") == "video/mp4":
                all_files.append(f)

    if not all_files:
        return None

    portrait_files = [f for f in all_files if f["height"] > f["width"]]
    pool = portrait_files if portrait_files else all_files

    best = max(pool, key=lambda f: f["width"] * f["height"])
    return best["link"]


def search_pexels(query: str) -> dict:
    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "orientation": "portrait", "per_page": 5},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def download_clip(url: str, dest: Path) -> None:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    dest.write_bytes(response.content)


def main():
    if not PEXELS_API_KEY:
        print("Falta PEXELS_API_KEY en .env")
        sys.exit(1)

    queries_path = SRC_DIR / "clip_queries.json"
    queries = json.loads(queries_path.read_text(encoding="utf-8"))

    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    clips = []
    for i, query in enumerate(queries):
        candidates = [query] + FALLBACK_QUERIES
        video_url = None
        used_query = None
        for q in candidates:
            data = search_pexels(q)
            video_url = pick_best_video(data)
            if video_url:
                used_query = q
                break

        if not video_url:
            print(f"  [{i}] Sin resultados para ninguna query, se omite")
            continue

        filename = f"clip_{i}.mp4"
        download_clip(video_url, CLIPS_DIR / filename)
        clips.append({"file": filename})
        print(f"  [{i}] '{used_query}' -> {filename}")

    clips_json_path = SRC_DIR / "clips.json"
    clips_json_path.write_text(
        json.dumps(clips, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nListo. {len(clips)} clips guardados en {CLIPS_DIR}, mapeo en {clips_json_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Paso 4: Correr el test para verificar que pasa**

Run: `python test_fetch_clips.py`
Expected: `Todos los tests pasaron.`

- [ ] **Paso 5: Crear `src/clip_queries.json`** con un término de búsqueda en inglés por cada una de las 10 oraciones de Task 1, en el mismo orden:

```json
[
  "man boxing punching bag",
  "close up flexing bicep muscle",
  "dark storm clouds timelapse",
  "man walking narrow alley shadow",
  "children playing park sunset",
  "skateboarder falling getting up",
  "man jumping cliff into ocean",
  "basketball player shooting hoops training",
  "man walking forward determined city street",
  "man reaching mountain summit sunrise"
]
```

- [ ] **Paso 6: Ejecutar la descarga real de clips**

Run: `python fetch_clips.py`
Expected: 10 líneas `[i] 'query' -> clip_i.mp4` (o el fallback usado si la query principal no tuvo resultados), y al final `Listo. 10 clips guardados en .../public/clips, mapeo en .../src/clips.json`.

Verificar:
```bash
ls public/clips/
cat src/clips.json
```
Expected: 10 archivos `clip_0.mp4` a `clip_9.mp4`, y `clips.json` con 10 entradas `{"file": "clip_N.mp4"}`.

- [ ] **Paso 7: Commit**

```bash
git add fetch_clips.py test_fetch_clips.py src/clip_queries.json src/clips.json public/clips/ .gitignore
git commit -m "feat: add Pexels b-roll clip fetcher for motivational videos"
```

Nota: si `public/clips/*.mp4` pesan mucho para el repo, agregar `public/clips/` a `.gitignore` antes del commit (ver Task 5, que también toca `.gitignore` si hace falta).

---

### Task 3: `MotivationalVideoBroll.tsx` — composición con fondo de video

**Files:**
- Create: `src/MotivationalVideoBroll.tsx`

**Interfaces:**
- Consumes: `src/captions_karaoke.json` (mismo tipo `Sentence[]` que usa `MotivationalVideoKaraoke.tsx`), `src/clips.json` (tipo `Clip[] = {file: string}[]`, de Task 2).
- Produces: componente `MotivationalVideoBroll: React.FC`, consumido por Task 4 en `Root.tsx`.

- [ ] **Paso 1: Crear el componente**

```tsx
import React from 'react';
import {
  AbsoluteFill,
  OffthreadVideo,
  Audio,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from 'remotion';
import captions from './captions_karaoke.json';
import clipsRaw from './clips.json';

interface WordTiming {
  word: string;
  start: number;
  end: number;
}

interface Sentence {
  start: number;
  end: number;
  words: WordTiming[];
}

interface Clip {
  file: string;
}

const sentences: Sentence[] = captions;
const clips: Clip[] = clipsRaw;

const KaraokeText: React.FC<{ sentence: Sentence }> = ({ sentence }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const startFrame = sentence.start * fps;
  const endFrame = sentence.end * fps;

  const opacity = interpolate(
    frame,
    [startFrame, startFrame + 6, endFrame - 6, endFrame],
    [0, 1, 1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  if (opacity === 0) return null;

  return (
    <div
      style={{
        opacity,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        alignContent: 'center',
        gap: '10px 16px',
        maxWidth: 900,
        padding: '0 60px',
      }}
    >
      {sentence.words.map((w, i) => {
        const wordStartFrame = w.start * fps;
        const wordEndFrame = w.end * fps;
        const isActive = frame >= wordStartFrame && frame < wordEndFrame;
        const isSpoken = frame >= wordEndFrame;

        const scale = interpolate(
          frame,
          [wordStartFrame, wordStartFrame + 3],
          [1, 1.14],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        ) * (isSpoken ? 1 / 1.14 : 1);

        const color = isActive
          ? '#FFD34D'
          : isSpoken
          ? '#FFFFFF'
          : 'rgba(255, 255, 255, 0.38)';

        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              transform: `scale(${scale})`,
              color,
              fontSize: 58,
              fontWeight: 600,
              fontFamily: 'Georgia, serif',
              fontStyle: 'italic',
              lineHeight: 1.3,
            }}
          >
            {w.word}
          </span>
        );
      })}
    </div>
  );
};

export const MotivationalVideoBroll: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const fadeOut = interpolate(
    frame,
    [durationInFrames - fps * 1.5, durationInFrames],
    [1, 0],
    { extrapolateLeft: 'clamp' }
  );
  const outerOpacity = Math.min(fadeIn, fadeOut);

  return (
    <AbsoluteFill style={{ background: '#000', opacity: outerOpacity }}>
      <Audio src={staticFile('voice.mp3')} volume={1} />

      {sentences.map((s, i) => {
        const clip = clips[i];
        const startFrame = Math.round(s.start * fps);
        const endFrame = Math.round(s.end * fps);
        const sentenceDuration = Math.max(endFrame - startFrame, 1);

        return (
          <Sequence key={i} from={startFrame} durationInFrames={sentenceDuration}>
            <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
              {clip && (
                <OffthreadVideo
                  src={staticFile(`clips/${clip.file}`)}
                  muted
                  loop
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                />
              )}
              <AbsoluteFill style={{ background: 'rgba(0,0,0,0.45)' }} />
              <KaraokeText sentence={s} />
            </AbsoluteFill>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
```

Nota de diseño: a diferencia de `MotivationalVideoKaraoke.tsx` (que monta todas las oraciones desde el frame 0 y usa opacidad para mostrar/ocultar texto), acá cada oración vive en su propio `<Sequence>`. Esto es necesario porque `OffthreadVideo` necesita un límite de montaje real para que cada clip empiece su propia reproducción en el frame 0 relativo a su secuencia — con opacidad sola, los 10 videos se reproducirían todos en paralelo desde el inicio.

- [ ] **Paso 2: Verificar tipos**

Run: `npm run typecheck`
Expected: sin errores.

- [ ] **Paso 3: Commit**

```bash
git add src/MotivationalVideoBroll.tsx
git commit -m "feat: add MotivationalVideoBroll component with per-sentence video background"
```

---

### Task 4: Registrar la composición y el script de build

**Files:**
- Modify: `src/Root.tsx`
- Modify: `package.json`

**Interfaces:**
- Consumes: `MotivationalVideoBroll` (de Task 3), `karaokeDuration` (variable ya existente en `Root.tsx`, calculada a partir de `captions_karaoke.json`).

- [ ] **Paso 1: Agregar el import y la composición en `Root.tsx`**

Modificar `src/Root.tsx:1-5` agregando el import:

```tsx
import React from 'react';
import { Composition, registerRoot } from 'remotion';
import { TopPlaces } from './TopPlaces';
import { MotivationalVideo } from './MotivationalVideo';
import { MotivationalVideoKaraoke } from './MotivationalVideoKaraoke';
import { MotivationalVideoBroll } from './MotivationalVideoBroll';
import captionsRaw from './captions.json';
import captionsKaraokeRaw from './captions_karaoke.json';
```

Y agregar la composición nueva después de `MotivacionalKaraoke` (dentro del `<>...</>` de `RemotionRoot`, usando `src/Root.tsx:38-45` como referencia de dónde está `MotivacionalKaraoke`):

```tsx
      <Composition
        id="MotivacionalBroll"
        component={MotivationalVideoBroll}
        durationInFrames={karaokeDuration}
        fps={30}
        width={1080}
        height={1920}
      />
```

- [ ] **Paso 2: Agregar el script de build en `package.json`**

Modificar `package.json` agregando, junto a `"build:karaoke"`:

```json
    "build:broll": "npx remotion render src/Root.tsx MotivacionalBroll out/motivacional_broll.mp4",
```

- [ ] **Paso 3: Verificar tipos**

Run: `npm run typecheck`
Expected: sin errores.

- [ ] **Paso 4: Commit**

```bash
git add src/Root.tsx package.json
git commit -m "feat: register MotivacionalBroll composition and build:broll script"
```

---

### Task 5: Render final y verificación visual

**Files:**
- No se crean archivos de código nuevos en este task (solo salida de render en `out/`).

**Interfaces:**
- Consumes: todo lo anterior (Tasks 1-4).

- [ ] **Paso 1: Verificar un frame intermedio antes del render completo**

Run: `npx remotion render src/Root.tsx MotivacionalBroll --frames=200 out/test_broll.png`
Expected: se genera `out/test_broll.png` sin errores. Revisar la imagen: debe verse el clip de video de fondo (no negro sólido), el velo oscuro, y el texto karaoke legible.

- [ ] **Paso 2: Render completo**

Run: `npm run build:broll`
Expected: `out/motivacional_broll.mp4` generado sin errores, duración ~63 segundos (10 oraciones, última termina en 61.64s + 2s de margen).

- [ ] **Paso 3: Verificar duración del archivo final**

Run: `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 out/motivacional_broll.mp4`
Expected: un valor cercano a `63` (segundos).

No se commitea `out/` (ya está en `.gitignore`).

---

## Self-Review

**Cobertura del spec:** guion nuevo (Task 1, ya hecho), `fetch_clips.py` + Pexels (Task 2), composición con fondo de video + overlay (Task 3), registro en Root.tsx + npm script (Task 4), render y verificación (Task 5). Todos los puntos del spec `2026-07-05-video-broll-miedo-design.md` están cubiertos.

**Placeholders:** ninguno — todo el código está completo, `clip_queries.json` tiene las 10 queries reales, `captions_karaoke.json` ya tiene contenido real documentado en Task 1.

**Consistencia de tipos:** `Clip` (`{file: string}`) se define igual en `fetch_clips.py` (implícito en el JSON que escribe) y en `MotivationalVideoBroll.tsx`. `Sentence`/`WordTiming` son idénticos a los de `MotivationalVideoKaraoke.tsx`. `pick_best_video` se usa igual en `fetch_clips.py` y en `test_fetch_clips.py`.
