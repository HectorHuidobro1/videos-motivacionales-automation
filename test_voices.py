#!/usr/bin/env python3
"""
test_voices.py — Genera muestras cortas con distintas voces/estilos de Gemini TTS
para comparar antes de elegir la definitiva.
"""

import os
import base64
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PROJECT_DIR = Path(__file__).parent
SAMPLES_DIR = PROJECT_DIR / "voice_samples"
SAMPLES_DIR.mkdir(exist_ok=True)

# Texto de prueba con etiquetas inline de estilo (tecnica tipo AI Studio "Master Storyteller")
TAGGED_TEXT = (
    "[reflexivo, pausado] Hay un momento en que dejas de mentirte a ti mismo. "
    "[pausa, tension baja] No llega con ruido. Llega en silencio. "
    "[firme, decidido] Y desde ahi, cada paso pesa distinto. "
    "[inspirador, resuelto] Porque ya no caminas por costumbre. Caminas por decision."
)

CONTEXT_PREFIX = (
    "Discurso motivacional intimo. Ritmo lento y deliberado, con pausas atmosfericas "
    "entre frases. Tono resuelto, calido y profundamente inspirador, casi susurrado "
    "en los momentos reflexivos y mas firme en los momentos de resolucion. "
    "Las palabras entre corchetes son notas de direccion para el tono y el ritmo — "
    "no deben pronunciarse en voz alta, solo usarse como guia de actuacion.\n\n"
)

SAMPLES = [
    {
        "name": "algenib_context_tags",
        "voice": "Algenib",
        "text": CONTEXT_PREFIX + TAGGED_TEXT,
    },
    {
        "name": "gacrux_context_tags",
        "voice": "Gacrux",
        "text": CONTEXT_PREFIX + TAGGED_TEXT,
    },
    {
        "name": "orus_context_tags",
        "voice": "Orus",
        "text": CONTEXT_PREFIX + TAGGED_TEXT,
    },
]


def generate_sample(name: str, voice: str, text: str):
    print(f"Generando muestra: {name} (voz={voice})...")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash-preview-tts:generateContent?key={GOOGLE_API_KEY}"
    )

    payload = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {"voiceName": voice}
                }
            },
        },
    }

    response = requests.post(url, json=payload, timeout=120)

    if response.status_code != 200:
        print(f"  Error ({response.status_code}): {response.text[:400]}")
        return

    data = response.json()
    try:
        part = data["candidates"][0]["content"]["parts"][0]
        audio_b64 = part["inlineData"]["data"]
        mime = part["inlineData"].get("mimeType", "audio/wav")
    except (KeyError, IndexError) as e:
        print(f"  Respuesta inesperada: {e}")
        return

    audio_bytes = base64.b64decode(audio_b64)
    raw_path = SAMPLES_DIR / f"{name}_raw.bin"
    mp3_path = SAMPLES_DIR / f"{name}.mp3"

    with open(raw_path, "wb") as f:
        f.write(audio_bytes)

    if mime == "audio/wav" or audio_bytes[:4] == b"RIFF":
        input_args = ["-i", str(raw_path)]
    else:
        input_args = ["-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(raw_path)]

    subprocess.run(
        ["ffmpeg", "-y"] + input_args + ["-codec:a", "libmp3lame", "-q:a", "2", str(mp3_path)],
        check=True,
        capture_output=True,
    )
    raw_path.unlink(missing_ok=True)
    print(f"  Guardado: {mp3_path}")


def main():
    for sample in SAMPLES:
        generate_sample(sample["name"], sample["voice"], sample["text"])

    print(f"\nMuestras listas en: {SAMPLES_DIR}")
    print("Reproducelas y dime cual te gusta mas.")


if __name__ == "__main__":
    main()
