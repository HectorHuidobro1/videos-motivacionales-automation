#!/usr/bin/env python3
"""
get_youtube_token.py — Corre una unica vez, de forma interactiva (abre el
navegador), para autorizar la cuenta de YouTube y guardar un refresh token
reutilizable en .env. Requiere youtube_client_secret.json en la raiz del
proyecto (descargado desde Google Cloud Console).
Uso: python automation/get_youtube_token.py
"""
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
PROJECT_DIR = Path(__file__).parent.parent


def main():
    client_secrets_path = PROJECT_DIR / "youtube_client_secret.json"
    if not client_secrets_path.exists():
        print(f"Falta {client_secrets_path}.")
        print("Descargalo desde Google Cloud Console (credenciales OAuth, tipo 'Desktop app').")
        return

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), SCOPES)
    creds = flow.run_local_server(port=0)

    env_path = PROJECT_DIR / ".env"
    existing = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    kept_lines = [
        line for line in existing.splitlines()
        if not line.startswith(("YOUTUBE_CLIENT_ID=", "YOUTUBE_CLIENT_SECRET=", "YOUTUBE_REFRESH_TOKEN="))
    ]
    kept_lines.append(f"YOUTUBE_CLIENT_ID={creds.client_id}")
    kept_lines.append(f"YOUTUBE_CLIENT_SECRET={creds.client_secret}")
    kept_lines.append(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
    env_path.write_text("\n".join(kept_lines) + "\n", encoding="utf-8")
    print("Listo. Credenciales guardadas en .env")


if __name__ == "__main__":
    main()
