# Diseño: Video motivacional "El miedo es un músculo" con fondo de video (b-roll)

**Fecha:** 2026-07-05
**Herramienta:** Remotion (React) + Gemini TTS + Groq Whisper + Pexels API
**Formato destino:** YouTube Shorts (vertical, hasta 3 min)

---

## Resumen

Nueva variante del pipeline de videos motivacionales: en vez de fondo negro sólido, cada oración del guion muestra un clip de video de stock (Pexels, gratuito) relacionado temáticamente, con un velo oscuro semi-transparente encima para mantener el texto legible. Reutiliza la voz (`Algenib`, -1 semitono) y el estilo de subtítulos karaoke ya existentes. El guion es nuevo, tomado de una parte distinta de la entrevista de Tony Robbins (miedo como músculo / la confianza se construye actuando) — no reutiliza texto de guiones anteriores.

---

## Guion

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

Fuente: transcripción de youtube.com/watch?v=5GyLU6o6K1g (entrevista Tony Robbins), pasaje sobre miedo/confianza — distinto del pasaje de "éxito vs. realización" ya usado en el guion anterior.

---

## Pipeline de datos

```
generate.py "guion..."          → public/voice.mp3 (voz Algenib -1 semitono)
generate.py --karaoke           → src/captions_karaoke.json (oraciones + timing)
fetch_clips.py (nuevo)          → public/clips/clip_0.mp4, clip_1.mp4, ...
                                 → src/clips.json (mapea índice de oración → archivo)
npm run build:broll             → out/motivacional_broll.mp4
```

### `fetch_clips.py` (nuevo script)

- Lee `src/captions_karaoke.json` (ya generado) para saber cuántas oraciones hay.
- Lee `src/clip_queries.json` (nuevo, armado a mano por Claude después de ver el texto real transcripto) — un array de strings, un término de búsqueda en inglés por oración, ej. `["boxer training gym", "child learning to walk falling", ...]`.
- Para cada término, llama a la API de Pexels Videos (`GET https://api.pexels.com/videos/search`), toma el primer resultado en orientación vertical/portrait si existe (si no, el de mayor resolución), descarga el archivo de video a `public/clips/clip_{i}.mp4`.
- Escribe `src/clips.json` = `[{"file": "clip_0.mp4"}, {"file": "clip_1.mp4"}, ...]`.
- Requiere `PEXELS_API_KEY` en `.env` (ya agregada).
- Si una búsqueda no devuelve resultados, hace fallback a un término más genérico ("motivation", "silhouette sunset") para no dejar un hueco.

---

## Composición Remotion nueva: `MotivationalVideoBroll.tsx`

Basada en `MotivationalVideoKaraoke.tsx` (mismo componente `KaraokeText` para las palabras), pero cada `<Sequence>` de oración agrega fondo de video en vez de `AbsoluteFill` negro:

```tsx
<Sequence from={startFrame} durationInFrames={...}>
  <AbsoluteFill>
    <OffthreadVideo
      src={staticFile(`clips/${clips[i].file}`)}
      muted
      loop
      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
    />
    <AbsoluteFill style={{ background: 'rgba(0,0,0,0.45)' }} />
    <KaraokeText sentence={sentence} />
  </AbsoluteFill>
</Sequence>
```

- `muted`: los clips no llevan audio propio, solo `voice.mp3` (pista única, como ya ocurre).
- `loop`: si el clip de Pexels dura menos que la oración, se repite en loop en vez de congelarse en el último frame.
- Overlay `rgba(0,0,0,0.45)`: mismo nivel elegido para las escenas de `PlaceScene` (consistente con `TopPlaces`).
- El texto karaoke (palabra por palabra, tamaño/colores) no cambia respecto a `MotivationalVideoKaraoke.tsx`.

### Registro en `Root.tsx`

Nueva composición `MotivacionalBroll`, misma lógica de duración dinámica que `MotivacionalKaraoke` (basada en el último timestamp de `captions_karaoke.json` + 2s).

### `package.json`

Nuevo script: `"build:broll": "npx remotion render src/Root.tsx MotivacionalBroll out/motivacional_broll.mp4"`.

---

## Estructura de archivos nueva/modificada

```
videos con remotion/
  fetch_clips.py                    ← nuevo
  src/
    clip_queries.json               ← nuevo (términos de búsqueda por oración)
    clips.json                      ← nuevo (generado por fetch_clips.py)
    MotivationalVideoBroll.tsx      ← nuevo
    Root.tsx                        ← agrega composición MotivacionalBroll
  public/
    clips/                          ← nuevo, videos descargados de Pexels
  package.json                      ← agrega build:broll
  .env                              ← agrega PEXELS_API_KEY (ya hecho)
```

---

## Fuera de alcance

- No se reemplaza la composición `MotivacionalKaraoke` existente (fondo negro) — queda como está, esta es una variante adicional.
- No se cachean/reutilizan clips entre distintos videos — cada render nuevo vuelve a buscar en Pexels (simplicidad sobre optimización, dado el volumen bajo de uso).
- No hay selección automática de vídeos por IA/embeddings — los términos de búsqueda se eligen a mano según el contenido real de cada oración transcripta.

---

## Criterios de éxito

- `python fetch_clips.py` descarga un clip por cada oración de `captions_karaoke.json` sin dejar huecos (fallback genérico si una búsqueda falla).
- `npm run build:broll` renderiza sin errores un video con fondo de video (no negro) sincronizado con el texto karaoke.
- El texto sigue siendo legible sobre el video de fondo gracias al overlay oscuro.
- El audio de voz permanece como única pista de audio (clips mudos).
