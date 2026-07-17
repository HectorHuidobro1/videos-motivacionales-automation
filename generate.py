#!/usr/bin/env python3
"""
generate.py — Genera voz + timestamps para videos motivacionales
Uso: python generate.py "Tu guion aqui"
  o: python generate.py --file script.txt
"""

import os
import sys
import json
import math
import base64
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PROJECT_DIR = Path(__file__).parent
PUBLIC_DIR = PROJECT_DIR / "public"
SRC_DIR = PROJECT_DIR / "src"

GEMINI_VOICE = "Algenib"  # Opciones: Puck, Charon, Kore, Fenrir, Aoede, Iapetus, Orus, Algenib
PITCH_SHIFT_SEMITONES = -1  # Ajuste fino sobre Algenib para un tono mas grave/misterioso

CONTEXT_PREFIX = (
    "Discurso motivacional intimo. Ritmo lento y deliberado, con pausas breves "
    "y naturales entre frases (nunca silencios largos). Tono resuelto, calido "
    "y profundamente inspirador.\n\n"
)


def generate_tts(text: str) -> Path:
    """Llama a Gemini TTS y guarda el audio en public/voice.mp3"""
    print("Generando voz con Gemini TTS...")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash-preview-tts:generateContent?key={GOOGLE_API_KEY}"
    )

    full_text = CONTEXT_PREFIX + text

    payload = {
        "contents": [{"parts": [{"text": full_text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {"voiceName": GEMINI_VOICE}
                }
            },
        },
    }

    response = requests.post(url, json=payload, timeout=120)

    if response.status_code != 200:
        print(f"Error Gemini TTS ({response.status_code}):")
        print(response.text[:800])
        sys.exit(1)

    data = response.json()

    try:
        part = data["candidates"][0]["content"]["parts"][0]
        audio_b64 = part["inlineData"]["data"]
        mime = part["inlineData"].get("mimeType", "audio/wav")
    except (KeyError, IndexError) as e:
        print(f"Respuesta inesperada de Gemini: {e}")
        print(json.dumps(data, indent=2)[:600])
        sys.exit(1)

    audio_bytes = base64.b64decode(audio_b64)
    raw_path = PUBLIC_DIR / "voice_raw.bin"
    mp3_path = PUBLIC_DIR / "voice.mp3"

    with open(raw_path, "wb") as f:
        f.write(audio_bytes)

    # Gemini puede devolver PCM crudo (s16le 24kHz mono) o WAV
    if mime == "audio/wav" or audio_bytes[:4] == b"RIFF":
        input_args = ["-i", str(raw_path)]
    else:
        # Raw PCM 16-bit little-endian 24kHz mono
        input_args = ["-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(raw_path)]

    # Baja el tono sin cambiar la velocidad: reescala la frecuencia de muestreo
    # (asetrate) y compensa la duracion resultante (atempo).
    factor = 2 ** (PITCH_SHIFT_SEMITONES / 12)
    pitch_filter = f"asetrate=24000*{factor},aresample=24000,atempo={1 / factor}"

    subprocess.run(
        ["ffmpeg", "-y"] + input_args + ["-af", pitch_filter, "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_path)],
        check=True,
        capture_output=True,
    )

    raw_path.unlink(missing_ok=True)
    print(f"Audio guardado: {mp3_path}")
    return mp3_path


MAX_WORDS_PER_PHRASE = 3
MAX_CHARS_PER_PHRASE = 18


def _group_words_into_phrases(words: list) -> list:
    """Agrupa palabras con timestamp en frases cortas (2-3 palabras) para
    subtitulos dinamicos tipo TikTok, en vez de oraciones completas estaticas."""
    phrases = []
    current = []

    def flush():
        if not current:
            return
        text = " ".join(w["word"] for w in current)
        phrases.append({
            "start": round(current[0]["start"], 3),
            "end": round(current[-1]["end"], 3),
            "text": text.strip(),
        })

    for w in words:
        current.append(w)
        char_count = sum(len(x["word"]) for x in current) + len(current) - 1
        if len(current) >= MAX_WORDS_PER_PHRASE or char_count >= MAX_CHARS_PER_PHRASE:
            flush()
            current = []
    flush()
    return phrases


WHISPER_MODEL_DIR = PROJECT_DIR / "automation" / "whisper_model"


def _transcribe_words_local(mp3_path: Path) -> list:
    """Transcribe con faster-whisper (modelo local empaquetado en el repo,
    sin llamadas de red a servicios de transcripcion ni descargas desde
    huggingface.co) y devuelve la lista plana de palabras con timestamp.
    Se usa cuando TRANSCRIBE_BACKEND=local, necesario en entornos que
    bloquean api.groq.com y huggingface.co (ej. el sandbox de los routines)."""
    print("Extrayendo timestamps con Whisper local (faster-whisper)...")

    from faster_whisper import WhisperModel

    model = WhisperModel(str(WHISPER_MODEL_DIR), device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(mp3_path), language="es", word_timestamps=True)

    words = []
    for segment in segments:
        for w in segment.words:
            words.append({
                "word": w.word.strip(),
                "start": float(w.start),
                "end": float(w.end),
            })
    return words


def _transcribe_words(mp3_path: Path) -> list:
    """Transcribe y devuelve la lista plana de palabras con timestamp. Usa
    Groq Whisper por defecto, o Whisper local si TRANSCRIBE_BACKEND=local."""
    if os.getenv("TRANSCRIBE_BACKEND") == "local":
        return _transcribe_words_local(mp3_path)

    print("Extrayendo timestamps con Groq Whisper...")

    import groq
    client = groq.Groq(api_key=GROQ_API_KEY)

    with open(mp3_path, "rb") as f:
        audio_bytes = f.read()

    transcription = client.audio.transcriptions.create(
        file=(mp3_path.name, audio_bytes),
        model="whisper-large-v3",
        response_format="verbose_json",
        timestamp_granularities=["word"],
        language="es",
    )

    words = []
    for w in transcription.words:
        word = w["word"] if isinstance(w, dict) else w.word
        start = w["start"] if isinstance(w, dict) else w.start
        end = w["end"] if isinstance(w, dict) else w.end
        words.append({
            "word": word.strip(),
            "start": float(start),
            "end": float(end),
        })
    return words


SENTENCE_ENDERS = (".", "!", "?", "...")


def _group_words_into_sentences(words: list) -> list:
    """Agrupa palabras en oraciones completas (para subtitulos tipo karaoke),
    conservando el timestamp individual de cada palabra."""
    sentences = []
    current = []

    for w in words:
        current.append(w)
        if w["word"].rstrip().endswith(SENTENCE_ENDERS):
            sentences.append(current)
            current = []
    if current:
        sentences.append(current)

    return [
        {
            "start": round(group[0]["start"], 3),
            "end": round(group[-1]["end"], 3),
            "words": [
                {"word": g["word"], "start": round(g["start"], 3), "end": round(g["end"], 3)}
                for g in group
            ],
        }
        for group in sentences
    ]


def get_timestamps(mp3_path: Path) -> list:
    """Genera frases cortas (2-3 palabras) con timestamp, para subtitulos dinamicos"""
    words = _transcribe_words(mp3_path)
    phrases = _group_words_into_phrases(words)

    captions_path = SRC_DIR / "captions.json"
    with open(captions_path, "w", encoding="utf-8") as f:
        json.dump(phrases, f, ensure_ascii=False, indent=2)

    print(f"Timestamps guardados: {captions_path} ({len(phrases)} frases cortas)")
    return phrases


def get_karaoke_captions(mp3_path: Path) -> list:
    """Genera oraciones completas con palabras cronometradas, para subtitulos tipo karaoke"""
    words = _transcribe_words(mp3_path)
    sentences = _group_words_into_sentences(words)

    captions_path = SRC_DIR / "captions_karaoke.json"
    with open(captions_path, "w", encoding="utf-8") as f:
        json.dump(sentences, f, ensure_ascii=False, indent=2)

    print(f"Timestamps karaoke guardados: {captions_path} ({len(sentences)} oraciones)")
    return sentences


def main():
    if len(sys.argv) < 2:
        print('Uso: python generate.py "Tu guion aqui"')
        print("  o: python generate.py --file script.txt")
        print("  o: python generate.py --recaption  (re-transcribe el audio ya generado)")
        sys.exit(1)

    if sys.argv[1] == "--recaption":
        mp3_path = PUBLIC_DIR / "voice.mp3"
        if not mp3_path.exists():
            print(f"No existe {mp3_path}. Genera el audio primero.")
            sys.exit(1)
        segments = get_timestamps(mp3_path)
        print("\nListo. Frases detectadas:")
        for seg in segments[:8]:
            print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
        if len(segments) > 8:
            print(f"  ... y {len(segments) - 8} mas")
        print("\nAhora ejecuta:")
        print("  npm run build:motivacional")
        return

    if sys.argv[1] == "--karaoke":
        mp3_path = PUBLIC_DIR / "voice.mp3"
        if not mp3_path.exists():
            print(f"No existe {mp3_path}. Genera el audio primero.")
            sys.exit(1)
        sentences = get_karaoke_captions(mp3_path)
        print("\nListo. Oraciones detectadas:")
        for s in sentences[:6]:
            text = " ".join(w["word"] for w in s["words"])
            print(f"  [{s['start']:.1f}s - {s['end']:.1f}s] {text}")
        if len(sentences) > 6:
            print(f"  ... y {len(sentences) - 6} mas")
        print("\nAhora ejecuta:")
        print("  npm run build:karaoke")
        return

    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Falta el path del archivo. Ejemplo: python generate.py --file script.txt")
            sys.exit(1)
        text = Path(sys.argv[2]).read_text(encoding="utf-8").strip()
    else:
        text = " ".join(sys.argv[1:]).strip()

    if not text:
        print("El guion esta vacio.")
        sys.exit(1)

    print(f"\nGuion ({len(text)} caracteres):")
    print(text[:120] + ("..." if len(text) > 120 else ""))
    print()

    PUBLIC_DIR.mkdir(exist_ok=True)

    mp3_path = generate_tts(text)
    segments = get_timestamps(mp3_path)

    print("\nListo. Segmentos detectados:")
    for seg in segments[:6]:
        print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
    if len(segments) > 6:
        print(f"  ... y {len(segments) - 6} mas")

    print("\nAhora ejecuta:")
    print("  npm run build:motivacional")


if __name__ == "__main__":
    main()
