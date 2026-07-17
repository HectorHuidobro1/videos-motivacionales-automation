#!/usr/bin/env python3
"""
fetch_clips.py — Descarga clips de video de Pexels para usar como fondo
en la composicion MotivacionalBroll, uno por cada oracion de captions_karaoke.json.
Uso: python fetch_clips.py
"""

import os
import sys
import json
import math
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PROJECT_DIR = Path(__file__).parent
PUBLIC_DIR = PROJECT_DIR / "public"
SRC_DIR = PROJECT_DIR / "src"
CLIPS_DIR = PUBLIC_DIR / "clips"

FPS = 30

FALLBACK_QUERIES = [
    "motivation silhouette sunset",
    "person walking determined slow motion",
    "dramatic clouds timelapse",
]


def pick_best_video(data: dict):
    """Elige el mejor archivo de video de una respuesta de Pexels: prefiere
    orientacion portrait (vertical), y entre esos el mas cercano a 1080x1920
    (evita tanto archivos muy chicos como 4K innecesariamente pesados)."""
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920
    TARGET_AREA = TARGET_WIDTH * TARGET_HEIGHT

    all_files = []
    for video in data.get("videos", []):
        for f in video.get("video_files", []):
            if f.get("file_type") == "video/mp4":
                all_files.append(f)

    if not all_files:
        return None

    portrait_files = [f for f in all_files if f["height"] > f["width"]]
    pool = portrait_files if portrait_files else all_files

    best = min(pool, key=lambda f: abs(f["width"] * f["height"] - TARGET_AREA))
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

    raw_path = dest.with_suffix(".raw.mp4")
    raw_path.write_bytes(response.content)

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(raw_path),
                "-r", "30", "-vsync", "cfr",
                "-g", "30", "-keyint_min", "30", "-sc_threshold", "0", "-bf", "0",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-an",
                str(dest),
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg error: {e.stderr.decode(errors='replace')}")
        raise
    raw_path.unlink(missing_ok=True)


def probe_duration_seconds(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def main():
    if not PEXELS_API_KEY:
        print("Falta PEXELS_API_KEY en .env")
        sys.exit(1)

    queries_path = SRC_DIR / "clip_queries.json"
    queries = json.loads(queries_path.read_text(encoding="utf-8"))

    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    clips_json_path = SRC_DIR / "clips.json"
    clips = []

    def persist():
        clips_json_path.write_text(
            json.dumps(clips, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    for i, query in enumerate(queries):
        candidates = [query] + FALLBACK_QUERIES
        video_url = None
        used_query = None
        for q in candidates:
            try:
                data = search_pexels(q)
            except requests.exceptions.RequestException as e:
                print(f"  [{i}] Error de red/API buscando '{q}', se prueba el siguiente: {e}")
                continue
            video_url = pick_best_video(data)
            if video_url:
                used_query = q
                break

        if not video_url:
            print(f"  [{i}] Sin resultados para ninguna query, se omite")
            persist()
            continue

        try:
            filename = f"clip_{i}.mp4"
            download_clip(video_url, CLIPS_DIR / filename)
            duration_seconds = probe_duration_seconds(CLIPS_DIR / filename)
            duration_in_frames = max(1, math.floor(duration_seconds * FPS))
            clips.append({"file": filename, "durationInFrames": duration_in_frames})
            print(f"  [{i}] '{used_query}' -> {filename} ({duration_in_frames} frames)")
        except (requests.exceptions.RequestException, subprocess.CalledProcessError) as e:
            print(f"  [{i}] Error de red/API/ffmpeg descargando, se omite: {e}")
        finally:
            persist()

    print(f"\nListo. {len(clips)} clips guardados en {CLIPS_DIR}, mapeo en {clips_json_path}")


def probe_only():
    clips_json_path = SRC_DIR / "clips.json"
    clips = json.loads(clips_json_path.read_text(encoding="utf-8"))
    for clip in clips:
        duration_seconds = probe_duration_seconds(CLIPS_DIR / clip["file"])
        clip["durationInFrames"] = max(1, math.floor(duration_seconds * FPS))
        print(f"  {clip['file']}: {clip['durationInFrames']} frames")
    clips_json_path.write_text(
        json.dumps(clips, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nActualizado {clips_json_path} con duraciones.")


def fix_framerate():
    clips_json_path = SRC_DIR / "clips.json"
    clips = json.loads(clips_json_path.read_text(encoding="utf-8"))
    for clip in clips:
        path = CLIPS_DIR / clip["file"]
        raw_path = path.with_suffix(".raw.mp4")
        if not raw_path.exists():
            path.rename(raw_path)
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(raw_path),
                    "-r", "30", "-vsync", "cfr",
                    "-g", "30", "-keyint_min", "30", "-sc_threshold", "0", "-bf", "0",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-an",
                    str(path),
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg error on {clip['file']}: {e.stderr.decode(errors='replace')}")
            raise
        raw_path.unlink(missing_ok=True)
        clip["durationInFrames"] = max(1, math.floor(probe_duration_seconds(path) * FPS))
        print(f"  {clip['file']}: re-encoded to 30fps, {clip['durationInFrames']} frames")
    clips_json_path.write_text(
        json.dumps(clips, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nActualizado {clips_json_path} con clips a 30fps constante.")


if __name__ == "__main__":
    if "--probe-only" in sys.argv:
        probe_only()
    elif "--fix-framerate" in sys.argv:
        fix_framerate()
    else:
        main()
