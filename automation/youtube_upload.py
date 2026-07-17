#!/usr/bin/env python3
"""
youtube_upload.py — Sube un video pendiente a YouTube y lo mueve a published/.
Uso: python automation/youtube_upload.py pending/2026-07-15/
"""
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).parent.parent
load_dotenv(PROJECT_DIR / ".env")


def build_snippet(metadata: dict) -> dict:
    return {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "public",
        },
    }


def upload_video(video_path: Path, metadata: dict) -> str:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = Credentials(
        None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token",
    )
    youtube = build("youtube", "v3", credentials=creds)
    body = build_snippet(metadata)
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    return response["id"]


def main():
    if len(sys.argv) != 2:
        print("Uso: python automation/youtube_upload.py pending/<carpeta>/")
        sys.exit(1)

    pending_dir = Path(sys.argv[1])
    metadata_path = pending_dir / "metadata.json"
    video_path = pending_dir / "video.mp4"

    if not metadata_path.exists() or not video_path.exists():
        print(f"Falta metadata.json o video.mp4 en {pending_dir}")
        sys.exit(1)

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    video_id = upload_video(video_path, metadata)
    print(f"Subido: https://youtube.com/watch?v={video_id}")

    published_dir = PROJECT_DIR / "published" / pending_dir.name
    published_dir.parent.mkdir(exist_ok=True)
    pending_dir.rename(published_dir)
    print(f"Movido a {published_dir}")


if __name__ == "__main__":
    main()
