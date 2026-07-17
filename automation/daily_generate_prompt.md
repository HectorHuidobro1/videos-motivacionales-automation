# Prompt del routine diario de generación

Trabajás en el repo de este proyecto (Remotion + Gemini TTS + Groq Whisper).
Tu única tarea es generar el video motivacional del día y dejarlo listo
para revisión humana — NO lo publiques en ningún lado, NO tenés acceso a
YouTube en esta tarea.

## Pasos

1. Instalá dependencias: `pip install -r requirements.txt` y `npm install`.
2. Elegí el tema del día:
   ```python
   import sys
   sys.path.insert(0, "automation")
   from rotation import get_next_topic, save_state
   from pathlib import Path
   index, topic = get_next_topic(Path("automation/topics.json"), Path("automation/rotation_state.json"))
   ```
3. Escribí un guion ORIGINAL en español (nunca copies texto de guiones anteriores del repo) sobre ese tema, de 80-150 palabras, con estas reglas (ya usadas en este proyecto, ver CLAUDE.md):
   - La primera frase debe ser un gancho directamente ligado al tema (afirmación fuerte, pregunta directa, o algo contraintuitivo) — no una introducción genérica.
   - Tono resuelto, cálido, inspirador.
4. Guardá el guion en un archivo temporal y corré:
   ```
   python generate.py --file <archivo_temporal>
   python generate.py --karaoke
   npm run build:karaoke
   ```
5. Armá un paquete de YouTube: un título principal + 2 alternativas, una descripción con hashtags, y una lista de tags — mismo estilo que ya se viene entregando en este proyecto (ver ejemplos en el historial de conversación / CLAUDE.md).
6. Creá la carpeta `pending/<fecha-de-hoy-YYYY-MM-DD>/`, movés ahí `out/motivacional_karaoke.mp4` como `video.mp4`, y escribís `metadata.json` con esta forma exacta:
   ```json
   {
     "topic": "<tema usado>",
     "guion": "<guion completo>",
     "title": "<título principal>",
     "title_alternatives": ["<alternativa 1>", "<alternativa 2>"],
     "description": "<descripción con hashtags>",
     "tags": ["<tag1>", "<tag2>", "..."]
   }
   ```
7. Actualizá el estado de rotación:
   ```python
   save_state(Path("automation/rotation_state.json"), index)
   ```
8. Commiteá y pusheá todo (incluyendo `pending/`, `automation/rotation_state.json`).
9. Enviá una notificación push al usuario con el tema del día y que el video está listo para revisar en `pending/`.

## Si algo falla

Si cualquier paso falla (error de generate.py, error de render, etc.), no dejes una carpeta `pending/` a medio escribir. Commiteá lo que sí haya avanzado (para no perder progreso) y enviá una notificación push explicando qué falló, en vez de fallar en silencio.
