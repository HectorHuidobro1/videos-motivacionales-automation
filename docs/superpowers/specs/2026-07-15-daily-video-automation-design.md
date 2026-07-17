# Diseño: Automatización diaria de videos motivacionales (generación + publicación en YouTube)

**Fecha:** 2026-07-15
**Alcance:** generación diaria automática (formato 1, fondo negro) + revisión por aprobación + publicación en YouTube. TikTok queda fuera de alcance hasta que se apruebe su API de publicación.

---

## Resumen

Hoy el pipeline de videos motivacionales (`generate.py`, `npm run build:karaoke`) se ejecuta manualmente en la PC del usuario, a partir de un tema o referencia que el usuario aporta cada vez. Este proyecto lo convierte en un proceso diario automático que corre en la nube (sin depender de que la PC esté prendida), eligiendo el tema de una lista rotativa, generando un guion original, renderizando el video, y dejándolo listo para que el usuario lo apruebe desde el chat antes de publicarlo en YouTube.

---

## Arquitectura

```
Repo privado en GitHub (nuevo)
  │
  ├── Routine diario (cron, 7am hora de Chile)
  │     1. Clona el repo
  │     2. Lee el estado de rotación de temas y elige el siguiente
  │     3. Escribe un guion original sobre ese tema (con gancho inicial)
  │     4. python generate.py --file <guion>
  │     5. python generate.py --karaoke
  │     6. npm run build:karaoke
  │     7. Mueve el mp4 + metadata (título/descripción/tags borrador) a pending/
  │     8. Actualiza el estado de rotación, commitea y pushea todo
  │     9. Envía notificación push al usuario
  │
  ├── Usuario revisa el video (desde cualquier chat, no necesita la PC)
  │     y responde algo como "dale, subilo"
  │
  └── Routine puntual de publicación (disparado manualmente, no en cron)
        1. Clona el repo
        2. Toma el video pendiente aprobado + su metadata
        3. Sube el video a YouTube por API (OAuth ya autorizado previamente)
        4. Mueve el registro de pending/ a published/, commitea y pushea
```

---

## Componentes

### 1. Repo privado en GitHub

- Se crea un repo privado nuevo y se sube el proyecto actual completo.
- **El `.env` se commitea dentro del repo** (decisión explícita del usuario: el repo es privado, riesgo aceptado). Si el repo alguna vez se hace público o se comparte, hay que rotar todas las API keys.
- Se agrega `requirements.txt` con las dependencias Python (`requests`, `python-dotenv`, `groq`) — hoy no existe y las dependencias están instaladas de forma ad-hoc en la PC del usuario.
- Riesgo a verificar en el plan: confirmar que el entorno del agente en la nube (Anthropic Cloud CCR) tiene Node.js, npm, Python y **ffmpeg** disponibles, o incluir su instalación como parte del prompt del routine si no vienen preinstalados.

### 2. Rotación de temas

Archivo nuevo `automation/topics.json` con la lista fija de 20 temas:

1. El miedo como músculo
2. Dinero y felicidad
3. Preparación antes del éxito
4. Disciplina vs. motivación
5. La comparación como ladrona de tiempo
6. Fracasar en público
7. Zona de confort
8. El costo de no decidir
9. Paciencia y resultados a largo plazo
10. Identidad y hábitos
11. Aceptar lo que no se puede controlar
12. Confianza en uno mismo
13. Rodearte de las personas correctas
14. El precio del éxito
15. Empezar aunque no estés listo
16. Confiar en el tiempo de Dios
17. La fe en medio de la incertidumbre
18. Gratitud como acto de fe
19. Dios no te abandona en el proceso
20. Fuiste creado con un propósito

Archivo nuevo `automation/rotation_state.json`: `{"last_used_index": N}`. Cada corrida diaria calcula `(last_used_index + 1) % 20`, usa ese tema, y actualiza el archivo antes de commitear. Al llegar al final de la lista, vuelve a empezar desde el tema 1.

### 3. Guion diario

El agente en la nube escribe un guion **original** (nunca reutiliza texto de guiones anteriores) sobre el tema del día, siguiendo las convenciones ya establecidas del proyecto (documentadas en `CLAUDE.md`):

- Primera frase como gancho, ligada directamente al tema.
- Tono resuelto, cálido, inspirador — consistente con `CONTEXT_PREFIX` de `generate.py`.
- Extensión similar a los guiones ya usados (~80-150 palabras, ~45-70 segundos hablado).

### 4. Generación y render (formato 1 únicamente)

Reutiliza el pipeline existente sin modificaciones: `generate.py --file`, `generate.py --karaoke`, `npm run build:karaoke`. Voz `Algenib` a -1 semitono (ya configurada, no se toca). No se usa el formato 2 (b-roll) en la automatización — depende de la API de Pexels y agrega un punto de falla adicional, fuera de alcance por ahora.

### 5. Carpeta `pending/`

Cada corrida diaria deja en `pending/YYYY-MM-DD/`:
- `video.mp4` (el render final)
- `metadata.json` con: tema usado, guion completo, y el paquete de YouTube (2-3 opciones de título, descripción con hashtags, tags) generado automáticamente siguiendo el mismo formato que se viene entregando manualmente.

### 6. Notificación y aprobación

Al terminar la corrida diaria, se envía una notificación push al usuario (tema del día + duración del video + que está listo en `pending/`). El usuario revisa cuando puede, desde cualquier dispositivo, y responde en un chat normal (no hace falta que sea con el routine, puede ser cualquier conversación) algo como "dale, subilo" o "no, descartalo".

### 7. Publicación en YouTube

Cuando el usuario aprueba, se dispara un **routine puntual** (`run_once_at`, no programado) que:
- Clona el repo.
- Toma el `pending/YYYY-MM-DD/` correspondiente.
- Sube el video vía YouTube Data API v3 (`videos.insert`), usando el título elegido, descripción y tags de `metadata.json`.
- Mueve la carpeta de `pending/` a `published/` y commitea.

### 8. Configuración única de YouTube OAuth (paso manual, una sola vez)

No se puede automatizar: requiere que el usuario inicie sesión con Google interactivamente. Se hace una sola vez, junto con el usuario:
1. Crear proyecto en Google Cloud, habilitar YouTube Data API v3.
2. Crear credenciales OAuth (client ID + secret).
3. Correr el flujo de autorización una vez para obtener un refresh token de larga duración.
4. Guardar client ID, secret y refresh token en el repo (junto al resto de las credenciales, mismo criterio aceptado en el punto 1).

Con el refresh token guardado, las subidas futuras no requieren volver a loguearse.

### 9. Prueba inicial

Una vez armado todo (repo, credenciales, routine diario, routine de publicación), se corre el routine diario manualmente una vez (sin esperar a las 7am del día siguiente) para probar el ciclo completo de punta a punta: generación → notificación → aprobación → publicación real en YouTube.

---

## Horario

7:00 AM hora de Chile (America/Santiago). En julio, Chile está en horario estándar (UTC-4), por lo que el cron equivalente es `0 11 * * *` (UTC). Esto se debe re-verificar al momento de crear el routine (la conversión de huso horario puede cambiar según la época del año si Chile alterna horario de verano).

---

## Fuera de alcance

- Publicación en TikTok (pendiente de aprobación de su Content Posting API — la aprobación puede tardar semanas y exige una interfaz con selector de privacidad, incompatible con un bot silencioso; se retoma en un proyecto aparte).
- Formato 2 (fondo b-roll) en la automatización diaria.
- Publicación 100% autónoma sin revisión humana (explícitamente descartada por el usuario).
- Selección de tema por IA sin lista fija, o por links que el usuario vaya aportando (se eligió la lista rotativa fija).
- Un mecanismo de secretos más seguro que commitear el `.env` al repo privado (el usuario aceptó el riesgo explícitamente).

---

## Criterios de éxito

- El routine diario corre sin intervención humana y deja un video + metadata listos en `pending/`.
- El usuario recibe la notificación push sin tener que revisar manualmente.
- Al aprobar por chat, el video sube a YouTube con el título/descripción/tags correctos, sin que el usuario haya tocado su PC en ningún momento del proceso.
- La rotación de temas avanza correctamente día a día y no repite un tema hasta completar la vuelta completa de 20.
- La prueba inicial (punto 9) completa el ciclo entero sin errores antes de dejarlo corriendo solo.
