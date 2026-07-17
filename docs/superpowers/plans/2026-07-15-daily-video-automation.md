# Automatización diaria de videos (generación + publicación YouTube) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended for this plan — see note below) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Nota sobre la elección de skill de ejecución:** este plan mezcla código puro (Tasks 1-4, aptas para TDD/subagentes) con pasos de infraestructura que requieren herramientas exclusivas de la sesión principal (`RemoteTrigger`, `PushNotification`) e interacción humana en vivo (crear el proyecto de Google Cloud, autorizar OAuth en el navegador) — Tasks 5-7. Por eso se recomienda ejecución inline en la sesión principal en vez de subagentes.

**Goal:** Automatizar la generación diaria de un video motivacional (formato 1, fondo negro) y su publicación en YouTube tras aprobación del usuario por chat, corriendo en la nube sin depender de la PC del usuario.

**Architecture:** Un repo privado de GitHub aloja el proyecto (incluyendo `.env`, decisión aceptada). Un routine en la nube corre todos los días a las 7am hora de Chile: rota el tema, escribe un guion original, genera voz+captions+render con el pipeline existente, deja el resultado en `pending/`, y notifica por push. Un segundo routine puntual (disparado manualmente cuando el usuario aprueba) sube el video a YouTube vía API usando credenciales OAuth guardadas de antemano.

**Tech Stack:** Python 3 (requests, python-dotenv, groq, google-auth-oauthlib, google-api-python-client), Node/Remotion (pipeline ya existente, sin cambios), YouTube Data API v3, Anthropic Cloud CCR (routines vía `RemoteTrigger`).

## Global Constraints

- Voz: `Algenib` con `PITCH_SHIFT_SEMITONES = -1` (ya configurado en `generate.py`, no modificar).
- Solo formato 1 (fondo negro, `MotivacionalKaraoke` / `npm run build:karaoke`) — no usar el formato b-roll en la automatización.
- Todo guion diario debe ser original (nunca reutilizar texto de guiones anteriores) y abrir con un gancho ligado al tema del día, según convención ya documentada en `CLAUDE.md`.
- El `.env` se commitea dentro del repo privado de GitHub (riesgo aceptado explícitamente por el usuario — ver spec).
- Horario: 7:00 AM hora de Chile (America/Santiago). En julio (horario estándar, UTC-4) equivale a `11:00 UTC` — **re-verificar la conversión al momento de crear el routine** (Task 7), no asumir que julio sigue vigente.
- No publicar nada en YouTube sin aprobación explícita del usuario por chat.

---

### Task 1: `requirements.txt` para portabilidad a la nube

**Files:**
- Create: `requirements.txt`

**Interfaces:**
- Produces: manifiesto de dependencias Python consumido por `pip install -r requirements.txt` en el entorno de la nube (Task 5/7).

- [ ] **Paso 1: Crear `requirements.txt`**

```
requests
python-dotenv
groq
google-auth
google-auth-oauthlib
google-api-python-client
```

- [ ] **Paso 2: Verificar que instala limpio**

Run: `pip install -r requirements.txt`
Expected: instala sin errores (los primeros tres paquetes ya están instalados localmente; los tres de Google son nuevos, necesarios para las Tasks 3-4).

- [ ] **Paso 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add requirements.txt for cloud portability"
```

---

### Task 2: Rotación de temas

**Files:**
- Create: `automation/topics.json`
- Create: `automation/rotation_state.json`
- Create: `automation/rotation.py`
- Create: `automation/test_rotation.py`

**Interfaces:**
- Produces: `get_next_topic(topics_path: Path, state_path: Path) -> tuple[int, str]`, `save_state(state_path: Path, index: int) -> None` — consumidos por el prompt del routine diario (Task 5).

- [ ] **Paso 1: Crear `automation/topics.json`**

```json
[
  "El miedo como músculo",
  "Dinero y felicidad",
  "Preparación antes del éxito",
  "Disciplina vs. motivación",
  "La comparación como ladrona de tiempo",
  "Fracasar en público",
  "Zona de confort",
  "El costo de no decidir",
  "Paciencia y resultados a largo plazo",
  "Identidad y hábitos",
  "Aceptar lo que no se puede controlar",
  "Confianza en uno mismo",
  "Rodearte de las personas correctas",
  "El precio del éxito",
  "Empezar aunque no estés listo",
  "Confiar en el tiempo de Dios",
  "La fe en medio de la incertidumbre",
  "Gratitud como acto de fe",
  "Dios no te abandona en el proceso",
  "Fuiste creado con un propósito"
]
```

- [ ] **Paso 2: Crear `automation/rotation_state.json` inicial**

```json
{
  "last_used_index": -1
}
```

(`-1` asegura que la primera corrida use el índice 0.)

- [ ] **Paso 3: Escribir el test que falla**

Crear `automation/test_rotation.py`:

```python
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rotation import get_next_topic, save_state


def test_first_run_picks_index_zero():
    with tempfile.TemporaryDirectory() as d:
        topics_path = Path(d) / "topics.json"
        state_path = Path(d) / "state.json"
        topics_path.write_text(json.dumps(["A", "B", "C"]), encoding="utf-8")
        index, topic = get_next_topic(topics_path, state_path)
        assert index == 0
        assert topic == "A"


def test_advances_to_next_index():
    with tempfile.TemporaryDirectory() as d:
        topics_path = Path(d) / "topics.json"
        state_path = Path(d) / "state.json"
        topics_path.write_text(json.dumps(["A", "B", "C"]), encoding="utf-8")
        save_state(state_path, 0)
        index, topic = get_next_topic(topics_path, state_path)
        assert index == 1
        assert topic == "B"


def test_wraps_around_at_end_of_list():
    with tempfile.TemporaryDirectory() as d:
        topics_path = Path(d) / "topics.json"
        state_path = Path(d) / "state.json"
        topics_path.write_text(json.dumps(["A", "B", "C"]), encoding="utf-8")
        save_state(state_path, 2)
        index, topic = get_next_topic(topics_path, state_path)
        assert index == 0
        assert topic == "A"


def test_missing_state_file_behaves_like_first_run():
    with tempfile.TemporaryDirectory() as d:
        topics_path = Path(d) / "topics.json"
        state_path = Path(d) / "state_does_not_exist.json"
        topics_path.write_text(json.dumps(["A", "B"]), encoding="utf-8")
        index, topic = get_next_topic(topics_path, state_path)
        assert index == 0
        assert topic == "A"


if __name__ == "__main__":
    test_first_run_picks_index_zero()
    test_advances_to_next_index()
    test_wraps_around_at_end_of_list()
    test_missing_state_file_behaves_like_first_run()
    print("Todos los tests pasaron.")
```

- [ ] **Paso 4: Correr el test para verificar que falla**

Run: `python automation/test_rotation.py`
Expected: `ModuleNotFoundError: No module named 'rotation'` (todavía no existe `rotation.py`).

- [ ] **Paso 5: Crear `automation/rotation.py`**

```python
"""
rotation.py — Elige el proximo tema de la lista rotativa y persiste el
indice usado, para que la generacion diaria nunca repita tema hasta
completar la vuelta completa.
"""
import json
from pathlib import Path


def get_next_topic(topics_path: Path, state_path: Path) -> tuple[int, str]:
    topics = json.loads(topics_path.read_text(encoding="utf-8"))

    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        last_index = state.get("last_used_index", -1)
    else:
        last_index = -1

    next_index = (last_index + 1) % len(topics)
    return next_index, topics[next_index]


def save_state(state_path: Path, index: int) -> None:
    state_path.write_text(
        json.dumps({"last_used_index": index}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
```

- [ ] **Paso 6: Correr el test para verificar que pasa**

Run: `python automation/test_rotation.py`
Expected: `Todos los tests pasaron.`

- [ ] **Paso 7: Commit**

```bash
git add automation/topics.json automation/rotation_state.json automation/rotation.py automation/test_rotation.py
git commit -m "feat: add topic rotation for daily video automation"
```

---

### Task 3: Script de subida a YouTube

**Files:**
- Create: `automation/youtube_upload.py`
- Create: `automation/test_youtube_upload.py`

**Interfaces:**
- Consumes: variables de entorno `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` (producidas por Task 4).
- Consumes: `pending/<carpeta>/video.mp4` y `pending/<carpeta>/metadata.json` con forma `{"topic": str, "guion": str, "title": str, "title_alternatives": [str], "description": str, "tags": [str]}` (producido por el prompt del routine diario, Task 5).
- Produces: `build_snippet(metadata: dict) -> dict`, `upload_video(video_path: Path, metadata: dict) -> str` (retorna el video ID de YouTube), consumidos por el prompt del routine de publicación (Task 6).

- [ ] **Paso 1: Escribir el test que falla**

Crear `automation/test_youtube_upload.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from youtube_upload import build_snippet


def test_build_snippet_includes_title_description_tags():
    metadata = {
        "topic": "El miedo como músculo",
        "guion": "texto del guion...",
        "title": "El miedo es un músculo",
        "title_alternatives": ["Otra opción de título"],
        "description": "Descripción de prueba con hashtags.",
        "tags": ["motivacion", "mentalidad fuerte"],
    }
    result = build_snippet(metadata)
    assert result["snippet"]["title"] == "El miedo es un músculo"
    assert result["snippet"]["description"] == "Descripción de prueba con hashtags."
    assert result["snippet"]["tags"] == ["motivacion", "mentalidad fuerte"]
    assert result["snippet"]["categoryId"] == "22"
    assert result["status"]["privacyStatus"] == "public"


if __name__ == "__main__":
    test_build_snippet_includes_title_description_tags()
    print("Todos los tests pasaron.")
```

- [ ] **Paso 2: Correr el test para verificar que falla**

Run: `python automation/test_youtube_upload.py`
Expected: `ModuleNotFoundError: No module named 'youtube_upload'`.

- [ ] **Paso 3: Crear `automation/youtube_upload.py`**

```python
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
```

- [ ] **Paso 4: Correr el test para verificar que pasa**

Run: `python automation/test_youtube_upload.py`
Expected: `Todos los tests pasaron.`

- [ ] **Paso 5: Commit**

```bash
git add automation/youtube_upload.py automation/test_youtube_upload.py
git commit -m "feat: add YouTube upload script for approved pending videos"
```

---

### Task 4: Script de autorización OAuth (paso único, interactivo)

**Files:**
- Create: `automation/get_youtube_token.py`
- Modify: `.gitignore` (agregar `youtube_client_secret.json` — no debe subirse, a diferencia del `.env`, porque Google lo entrega como archivo descargable y no hace falta versionarlo, el `.env` ya captura lo necesario una vez corrido este script)

**Interfaces:**
- Produces: variables `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` agregadas a `.env`, consumidas por `automation/youtube_upload.py` (Task 3).

**Este task requiere acción humana en vivo — no es delegable a un subagente.** Antes de correr el script, el usuario (guiado en la sesión) debe:
1. Crear un proyecto en [Google Cloud Console](https://console.cloud.google.com/).
2. Habilitar "YouTube Data API v3" en ese proyecto.
3. Crear credenciales OAuth de tipo "Desktop app".
4. Descargar el JSON de credenciales y guardarlo como `youtube_client_secret.json` en la raíz del proyecto.

- [ ] **Paso 1: Agregar `youtube_client_secret.json` al `.gitignore`**

Modificar `.gitignore`:

```
node_modules
.env
out/
.superpowers/
public/clips/
youtube_client_secret.json
```

- [ ] **Paso 2: Crear `automation/get_youtube_token.py`**

```python
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
```

- [ ] **Paso 3: Guiar al usuario a crear las credenciales en Google Cloud Console** (ver los 4 puntos arriba)

- [ ] **Paso 4: Correr el script y completar el login interactivo**

Run: `python automation/get_youtube_token.py`
Expected: se abre el navegador, el usuario inicia sesión con la cuenta de YouTube donde quiere publicar, acepta los permisos, y la terminal imprime `Listo. Credenciales guardadas en .env`.

- [ ] **Paso 5: Verificar que las variables quedaron en `.env`**

Run: `grep YOUTUBE .env` (o revisar el archivo)
Expected: aparecen las 3 líneas `YOUTUBE_CLIENT_ID=`, `YOUTUBE_CLIENT_SECRET=`, `YOUTUBE_REFRESH_TOKEN=` con valores no vacíos.

- [ ] **Paso 6: Commit (sin el archivo de credenciales, que ya está en .gitignore)**

```bash
git add automation/get_youtube_token.py .gitignore
git commit -m "feat: add one-time YouTube OAuth authorization script"
```

---

### Task 5: Repo en GitHub + prompt del routine diario

**Files:**
- Create: `automation/daily_generate_prompt.md` (contenido del prompt, referencia versionada — el texto real se pega en el routine vía `RemoteTrigger` en Task 7)
- Create: repo privado en GitHub (fuera del árbol de archivos local)

**Interfaces:**
- Consumes: `automation/rotation.py` (Task 2), `generate.py`/`npm run build:karaoke` (pipeline existente, sin cambios).
- Produces: `pending/YYYY-MM-DD/video.mp4` + `pending/YYYY-MM-DD/metadata.json`, consumidos por `automation/youtube_upload.py` (Task 3) vía el routine de publicación (Task 6).

- [ ] **Paso 1: Crear el repo privado en GitHub**

Guiar al usuario (o usar `gh repo create` si tiene `gh` autenticado) para crear un repo privado nuevo, por ejemplo `videos-motivacionales-automation`.

Run: `gh repo create videos-motivacionales-automation --private --source=. --remote=origin` (si `gh` está disponible y autenticado)
Expected: repo creado y remote `origin` agregado.

- [ ] **Paso 2: Forzar el agregado del `.env` (normalmente ignorado) para este push**

```bash
git add -f .env
git commit -m "chore: include .env for cloud routine access (private repo, accepted risk)"
```

- [ ] **Paso 3: Pushear todo al repo**

Run: `git push -u origin master`
Expected: el repo remoto queda con todo el historial y el `.env` incluido.

- [ ] **Paso 4: Escribir `automation/daily_generate_prompt.md`**

```markdown
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
```

- [ ] **Paso 5: Commit**

```bash
git add automation/daily_generate_prompt.md
git commit -m "docs: add daily generation routine prompt"
git push
```

---

### Task 6: Prompt del routine de publicación

**Files:**
- Create: `automation/publish_prompt.md`

**Interfaces:**
- Consumes: `automation/youtube_upload.py` (Task 3), `pending/YYYY-MM-DD/` (producido por Task 5).

- [ ] **Paso 1: Escribir `automation/publish_prompt.md`**

```markdown
# Prompt del routine de publicación (disparado manualmente, no en cron)

Trabajás en el repo de este proyecto. El usuario ya aprobó el video
pendiente más reciente — tu única tarea es publicarlo en YouTube.

## Pasos

1. Instalá dependencias: `pip install -r requirements.txt`.
2. Encontrá la carpeta más reciente dentro de `pending/` (por nombre de
   fecha, la más alta ordenada como string `YYYY-MM-DD` funciona).
3. Corré: `python automation/youtube_upload.py pending/<esa-carpeta>/`
4. Verificá que imprimió una URL de `https://youtube.com/watch?v=...` y
   que la carpeta se movió a `published/<esa-carpeta>/`.
5. Commiteá y pusheá el cambio (la carpeta movida).
6. Enviá una notificación push al usuario con la URL del video publicado.

## Si algo falla

Si la subida falla (error de API, credenciales vencidas, etc.), NO
muevas la carpeta de `pending/` a `published/` — dejala en `pending/`
tal cual, commiteá cualquier log útil, y enviá una notificación push
explicando el error para que el usuario decida cómo seguir.
```

- [ ] **Paso 2: Commit**

```bash
git add automation/publish_prompt.md
git commit -m "docs: add publish routine prompt"
git push
```

---

### Task 7: Crear los routines en la nube y correr la prueba end-to-end

**Files:** ninguno nuevo — este task usa las herramientas `RemoteTrigger` y `PushNotification` directamente desde la sesión principal (no delegable a subagente, según nota al inicio del plan).

**Interfaces:**
- Consumes: todo lo anterior (Tasks 1-6).

- [ ] **Paso 1: Re-verificar la hora UTC actual**

Run: `date -u +%Y-%m-%dT%H:%M:%SZ`
Expected: usar este resultado (no un valor asumido) para confirmar que 7:00 AM hora de Chile (America/Santiago) sigue correspondiendo a `11:00 UTC` en la fecha real de ejecución de este paso.

- [ ] **Paso 2: Crear el routine diario con `RemoteTrigger`**

`action: "create"` con:
- `name`: `"Generación diaria de video motivacional"`
- `cron_expression`: `"0 11 * * *"` (o el valor corregido según el Paso 1)
- `job_config.ccr.session_context.sources`: el repo de GitHub creado en Task 5
- `job_config.ccr.session_context.allowed_tools`: incluir `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, y `PushNotification`
- `job_config.ccr.events[].data.message.content`: el contenido completo de `automation/daily_generate_prompt.md`

Expected: la llamada devuelve un `trigger_id`; anotarlo.

- [ ] **Paso 3: Correr el routine diario ahora mismo (prueba, sin esperar al cron)**

`action: "run"` con el `trigger_id` del Paso 2.
Expected: el routine corre, genera el video, y el usuario recibe la notificación push. Verificar en el repo remoto que `pending/<fecha-de-hoy>/video.mp4` y `metadata.json` existen.

- [ ] **Paso 4: Esperar la aprobación del usuario por chat**

El usuario revisa el video (se le puede compartir el `metadata.json` o describírselo) y responde algo como "dale, subilo" en el chat.

- [ ] **Paso 5: Crear y correr el routine de publicación**

`action: "create"` con:
- `name`: `"Publicación YouTube — <fecha>"`
- `run_once_at`: unos minutos en el futuro desde la hora actual (re-verificada con `date -u`)
- Mismo repo, `allowed_tools` incluyendo `PushNotification`
- `events[].data.message.content`: el contenido completo de `automation/publish_prompt.md`

Luego `action: "run"` con el `trigger_id` recién creado (no hace falta esperar al `run_once_at` si se quiere probar ya).

Expected: el routine corre, el video queda publicado en YouTube (público), el usuario recibe una notificación push con la URL, y `pending/<fecha>/` se movió a `published/<fecha>/` en el repo.

- [ ] **Paso 6: Confirmar con el usuario que el video es visible en YouTube**

Pedirle al usuario que abra la URL recibida y confirme que el video se ve y suena bien.

---

## Self-Review

**Cobertura del spec:** repo privado (Task 5), rotación de temas (Task 2), guion original con gancho (prompt de Task 5), pipeline de generación sin cambios (prompt de Task 5), carpeta `pending/` con metadata (prompt de Task 5), notificación push (Tasks 5-7), aprobación por chat (Task 7 Paso 4), publicación YouTube (Tasks 3, 4, 6, 7), horario 7am Chile (Task 7 Paso 1-2), prueba inicial sin esperar al día siguiente (Task 7 Paso 3 y 5). Todos los puntos del spec están cubiertos.

**Placeholders:** ninguno — todo el código y los prompts están completos, sin TBD.

**Consistencia de tipos:** `metadata.json` tiene la misma forma exacta en el prompt de Task 5 (quien lo escribe) y en `youtube_upload.py`/su test (Task 3, quien lo lee) — `topic`, `guion`, `title`, `title_alternatives`, `description`, `tags`. `get_next_topic`/`save_state` se usan con la misma firma en Task 2 (definición) y en el prompt de Task 5 (consumo).
