# Diseño: TOP 5 Lugares Asombrosos del Mundo — Video Reel/TikTok

**Fecha:** 2026-06-28
**Herramienta:** Remotion (React)
**Formato destino:** TikTok / Instagram Reels

---

## Resumen

Video vertical de 60 segundos estilo cinematográfico oscuro que presenta los 5 lugares más asombrosos del mundo. Cada lugar tiene su propia escena con efecto Ken Burns (zoom lento sobre imagen de fondo), overlay oscuro y animaciones de texto con `spring()`. Se incluye música de fondo vía archivo `public/music.mp3`.

---

## Especificaciones técnicas

| Parámetro | Valor |
|---|---|
| Resolución | 1080 × 1920 px (9:16 vertical) |
| FPS | 30 |
| Duración total | 60 segundos (1800 frames) |
| Librería | Remotion 4.x |
| Node.js requerido | >= 18 |

---

## Estructura de escenas

| Escena | Inicio (frame) | Fin (frame) | Duración |
|---|---|---|---|
| Intro | 0 | 150 | 5 seg |
| #5 Gran Cañón, USA | 150 | 450 | 10 seg |
| #4 Las Maldivas | 450 | 750 | 10 seg |
| #3 Aurora Boreal, Islandia | 750 | 1050 | 10 seg |
| #2 Machu Picchu, Perú | 1050 | 1350 | 10 seg |
| #1 Cueva Waitomo, Nueva Zelanda | 1350 | 1650 | 10 seg |
| Outro | 1650 | 1800 | 5 seg |

---

## Contenido de cada lugar

### #5 — Gran Cañón del Colorado, USA
- **Imagen:** Unsplash — paisaje aéreo del cañón al atardecer
- **Dato curioso:** "Tiene 446 km de largo y hasta 1,800 metros de profundidad"

### #4 — Las Maldivas, Océano Índico
- **Imagen:** Unsplash — aguas turquesa con bungalows sobre el agua
- **Dato curioso:** "Es el país más bajo del mundo, a solo 1.5 metros sobre el mar"

### #3 — Aurora Boreal, Islandia
- **Imagen:** Unsplash — cielo verde/morado sobre paisaje nevado
- **Dato curioso:** "Solo visible entre septiembre y marzo, en zonas de oscuridad total"

### #2 — Machu Picchu, Perú
- **Imagen:** Unsplash — ciudadela inca entre nubes y montañas
- **Dato curioso:** "Construida en el siglo XV a 2,430 metros de altitud"

### #1 — Cueva Waitomo, Nueva Zelanda
- **Imagen:** Unsplash — cueva con miles de luciérnagas bioluminiscentes
- **Dato curioso:** "Miles de luciérnagas crean una galaxia natural bajo tierra"

---

## Animación por escena PlaceScene (10 seg = 300 frames)

```
Frame 0–30   (1s):  fade in desde negro (opacity 0→1)
Frame 0–300  (10s): Ken Burns — imagen escala de 1.0 → 1.15 (interpolate lineal)
Frame 30–60  (1s):  número "#5" sube desde Y+80 con spring()
Frame 60–120 (2s):  nombre del lugar fade in + slide leve desde abajo
Frame 120–180(2s):  país/ubicación aparece (texto pequeño, letra espaciada)
Frame 180–240(2s):  dato curioso aparece en cursiva, tamaño mediano
Frame 270–300(1s):  fade a negro (opacity 1→0)
```

---

## Escena Intro (5 seg = 150 frames)

```
Frame 0–30:   fondo negro, partícula de luz centellea
Frame 30–90:  "TOP 5" entra con scale spring (grande, bold)
Frame 90–150: "LUGARES ASOMBROSOS DEL MUNDO" fade in debajo, letra espaciada
```

---

## Escena Outro (5 seg = 150 frames)

```
Frame 0–60:   "¿Cuál visitarías?" fade in centrado
Frame 60–120: "Comenta 👇" aparece debajo
Frame 120–150: fade a negro general
```

---

## Paleta de colores

| Elemento | Color |
|---|---|
| Fondo base | `#000000` |
| Overlay imagen | `rgba(0,0,0,0.45)` |
| Número ranking | `#FFD700` (dorado) |
| Nombre lugar | `#FFFFFF` |
| Ubicación | `rgba(255,255,255,0.7)` |
| Dato curioso | `rgba(255,255,255,0.85)` cursiva |

---

## Tipografía

- **Número:** 120px, weight 900, font Montserrat o similar sans-serif
- **Nombre lugar:** 64px, weight 700, uppercase, letter-spacing 4px
- **Ubicación:** 28px, weight 400, letter-spacing 6px, uppercase
- **Dato curioso:** 30px, weight 400, italic

---

## Audio

- Archivo: `public/music.mp3` (el usuario lo provee)
- Componente: `<Audio src={staticFile('music.mp3')} volume={0.7} />`
- Sin efectos de sonido adicionales

---

## Estructura de archivos

```
pronado remotion/
  src/
    Root.tsx            ← registra composición TopPlaces
    TopPlaces.tsx       ← composición principal, orquesta escenas
    Intro.tsx           ← escena de apertura 5 seg
    PlaceScene.tsx      ← componente reutilizable por lugar
    Outro.tsx           ← escena de cierre 5 seg
  public/
    music.mp3           ← el usuario coloca su canción aquí
  package.json
  remotion.config.ts
```

---

## Dependencias

- `remotion` >= 4.0
- `@remotion/cli` >= 4.0
- Node.js >= 18

---

## Criterios de éxito

- El video se renderiza en 60 segundos exactos a 30 FPS
- Las transiciones Ken Burns se ven fluidas sin saltos
- El texto es legible en pantalla de móvil (mínimo 28px)
- El audio sincroniza desde el frame 0
- Funciona con `npx remotion preview` sin errores
