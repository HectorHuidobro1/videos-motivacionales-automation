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
