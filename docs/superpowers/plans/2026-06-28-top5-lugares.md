# TOP 5 Lugares Asombrosos — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear un video vertical de 60 segundos estilo cinematográfico oscuro con efecto Ken Burns para TikTok/Reels usando Remotion.

**Architecture:** Composición Remotion de 1800 frames a 30 FPS con 7 escenas en secuencia: Intro → 5 PlaceScenes reutilizables → Outro. Cada PlaceScene recibe sus datos como props y anima imagen + texto independientemente usando `interpolate()` y `spring()`.

**Tech Stack:** Remotion 4.x, React 18, TypeScript 5, Node.js >= 18

## Global Constraints

- Node.js >= 18 (requerido por Remotion 4.x)
- Resolución: 1080×1920 px (9:16 vertical)
- Duración exacta: 1800 frames a 30 FPS (60 segundos)
- Paleta: fondo `#000`, dorado `#FFD700`, blanco `#FFFFFF`
- Fuentes del sistema: Arial/Arial Black/Georgia (sin Google Fonts para evitar dependencias externas)
- Imágenes: URLs de Unsplash vía `<Img>` de Remotion
- Audio: `public/music.mp3` — el usuario debe colocar el archivo ahí manualmente

---

## Mapa de archivos

| Archivo | Responsabilidad |
|---|---|
| `package.json` | Dependencias y scripts |
| `tsconfig.json` | Configuración TypeScript |
| `remotion.config.ts` | Entry point para el CLI |
| `src/Root.tsx` | Registra la composición con `registerRoot` |
| `src/TopPlaces.tsx` | Orquesta todas las escenas con `<Sequence>` + `<Audio>` |
| `src/Intro.tsx` | Escena de apertura 5 seg (frames 0–150) |
| `src/PlaceScene.tsx` | Componente reutilizable por cada lugar |
| `src/Outro.tsx` | Escena de cierre 5 seg (frames 1650–1800) |
| `public/music.mp3` | Audio de fondo — el usuario lo provee |

---

## Task 1: Prerequisitos y scaffolding del proyecto

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `remotion.config.ts`

**Interfaces:**
- Produces: proyecto instalable con `npm install`, comandos `start` (preview) y `build` (render)

- [ ] **Step 1: Verificar Node.js >= 18**

```powershell
node --version
```

Si el resultado es menor a `v18`, instala Node 18 LTS desde https://nodejs.org antes de continuar. El proyecto NO funcionará con Node 16.

- [ ] **Step 2: Crear `package.json`**

```json
{
  "name": "pronado-remotion",
  "version": "1.0.0",
  "scripts": {
    "start": "npx remotion preview src/Root.tsx",
    "build": "npx remotion render src/Root.tsx TopPlaces out/video.mp4",
    "typecheck": "npx tsc --noEmit"
  },
  "dependencies": {
    "@remotion/cli": "^4.0.0",
    "remotion": "^4.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.0.0"
  }
}
```

- [ ] **Step 3: Crear `tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx"
  },
  "include": ["src", "remotion.config.ts"]
}
```

- [ ] **Step 4: Crear `remotion.config.ts`**

```ts
import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
```

- [ ] **Step 5: Crear carpeta `src` y `public`**

```powershell
New-Item -ItemType Directory -Force src
New-Item -ItemType Directory -Force public
```

- [ ] **Step 6: Instalar dependencias**

```powershell
npm install
```

Esperar a que termine. Ignorar warnings de peer deps si los hay.

- [ ] **Step 7: Verificar instalación**

```powershell
npx remotion --version
```

Debe imprimir algo como `4.0.x`. Si hay error, revisar que Node >= 18 esté activo.

- [ ] **Step 8: Commit**

```powershell
git init
git add package.json tsconfig.json remotion.config.ts
git commit -m "chore: scaffold remotion project"
```

---

## Task 2: Root.tsx — registro de composición

**Files:**
- Create: `src/Root.tsx`

**Interfaces:**
- Consumes: `TopPlaces` de `./TopPlaces` (aún no existe; se creará en Task 6)
- Produces: `registerRoot()` con composición `"TopPlaces"` de 1800 frames, 30 FPS, 1080×1920

- [ ] **Step 1: Crear `src/Root.tsx`**

```tsx
import React from 'react';
import { Composition, registerRoot } from 'remotion';
import { TopPlaces } from './TopPlaces';

const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="TopPlaces"
      component={TopPlaces}
      durationInFrames={1800}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};

registerRoot(RemotionRoot);
```

- [ ] **Step 2: Crear `src/TopPlaces.tsx` temporal para que TypeScript no falle**

```tsx
import React from 'react';
import { AbsoluteFill } from 'remotion';

export const TopPlaces: React.FC = () => {
  return <AbsoluteFill style={{ background: '#000' }} />;
};
```

- [ ] **Step 3: Verificar tipos**

```powershell
npm run typecheck
```

Resultado esperado: sin errores.

- [ ] **Step 4: Commit**

```powershell
git add src/Root.tsx src/TopPlaces.tsx
git commit -m "feat: add root composition and placeholder TopPlaces"
```

---

## Task 3: PlaceScene.tsx — escena reutilizable con Ken Burns

**Files:**
- Create: `src/PlaceScene.tsx`

**Interfaces:**
- Consumes: nada externo
- Produces: `PlaceScene` — props: `{ rank: number; name: string; location: string; fact: string; imageUrl: string }`

- [ ] **Step 1: Crear `src/PlaceScene.tsx`**

```tsx
import React from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

interface PlaceSceneProps {
  rank: number;
  name: string;
  location: string;
  fact: string;
  imageUrl: string;
}

export const PlaceScene: React.FC<PlaceSceneProps> = ({
  rank,
  name,
  location,
  fact,
  imageUrl,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Ken Burns: zoom 1.0 → 1.15 durante toda la escena (300 frames)
  const scale = interpolate(frame, [0, 300], [1, 1.15], {
    extrapolateRight: 'clamp',
  });

  // Fade in (frames 0-30) y fade out (frames 270-300)
  const opacity = interpolate(frame, [0, 30, 270, 300], [0, 1, 1, 0], {
    extrapolateRight: 'clamp',
  });

  // Número ranking: spring desde frame 30
  const rankProgress = spring({
    frame: frame - 30,
    fps,
    config: { damping: 12, stiffness: 100 },
  });
  const rankY = interpolate(rankProgress, [0, 1], [80, 0]);
  const rankOpacity = interpolate(frame, [30, 60], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Nombre: fade + slide desde frame 60
  const nameOpacity = interpolate(frame, [60, 90], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const nameY = interpolate(frame, [60, 90], [20, 0], {
    extrapolateRight: 'clamp',
  });

  // Ubicación: desde frame 120
  const locationOpacity = interpolate(frame, [120, 150], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Dato curioso: desde frame 180
  const factOpacity = interpolate(frame, [180, 210], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ opacity }}>
      {/* Imagen con Ken Burns */}
      <AbsoluteFill>
        <Img
          src={imageUrl}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${scale})`,
            transformOrigin: 'center center',
          }}
        />
      </AbsoluteFill>

      {/* Overlay oscuro */}
      <AbsoluteFill style={{ background: 'rgba(0,0,0,0.45)' }} />

      {/* Contenido centrado */}
      <AbsoluteFill
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '0 60px',
        }}
      >
        {/* Número ranking */}
        <div
          style={{
            transform: `translateY(${rankY}px)`,
            opacity: rankOpacity,
            fontSize: 120,
            fontWeight: 900,
            color: '#FFD700',
            fontFamily: 'Arial Black, Arial, sans-serif',
            lineHeight: 1,
          }}
        >
          #{rank}
        </div>

        {/* Nombre del lugar */}
        <div
          style={{
            transform: `translateY(${nameY}px)`,
            opacity: nameOpacity,
            fontSize: 64,
            fontWeight: 700,
            color: '#FFFFFF',
            fontFamily: 'Arial, sans-serif',
            textTransform: 'uppercase',
            letterSpacing: 4,
            textAlign: 'center',
            marginTop: 16,
          }}
        >
          {name}
        </div>

        {/* Ubicación */}
        <div
          style={{
            opacity: locationOpacity,
            fontSize: 28,
            fontWeight: 400,
            color: 'rgba(255,255,255,0.7)',
            fontFamily: 'Arial, sans-serif',
            textTransform: 'uppercase',
            letterSpacing: 6,
            marginTop: 12,
          }}
        >
          {location}
        </div>

        {/* Dato curioso */}
        <div
          style={{
            opacity: factOpacity,
            fontSize: 30,
            fontWeight: 400,
            color: 'rgba(255,255,255,0.85)',
            fontFamily: 'Georgia, serif',
            fontStyle: 'italic',
            textAlign: 'center',
            marginTop: 40,
            maxWidth: 900,
            lineHeight: 1.6,
          }}
        >
          &ldquo;{fact}&rdquo;
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Verificar tipos**

```powershell
npm run typecheck
```

Resultado esperado: sin errores.

- [ ] **Step 3: Commit**

```powershell
git add src/PlaceScene.tsx
git commit -m "feat: add PlaceScene component with Ken Burns and text animations"
```

---

## Task 4: Intro.tsx — escena de apertura

**Files:**
- Create: `src/Intro.tsx`

**Interfaces:**
- Consumes: nada externo
- Produces: `Intro` — sin props, dura 150 frames internamente

- [ ] **Step 1: Crear `src/Intro.tsx`**

```tsx
import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // "TOP 5" entra con spring
  const top5Scale = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 80 },
  });
  const top5Opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Subtítulo aparece desde frame 60
  const subtitleOpacity = interpolate(frame, [60, 100], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Fade out general al final (frames 120-150)
  const outerOpacity = interpolate(frame, [120, 150], [1, 0], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: '#000',
        opacity: outerOpacity,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      {/* TOP 5 */}
      <div
        style={{
          transform: `scale(${top5Scale})`,
          opacity: top5Opacity,
          fontSize: 160,
          fontWeight: 900,
          color: '#FFD700',
          fontFamily: 'Arial Black, Arial, sans-serif',
          letterSpacing: -2,
          lineHeight: 1,
        }}
      >
        TOP 5
      </div>

      {/* LUGARES ASOMBROSOS */}
      <div
        style={{
          opacity: subtitleOpacity,
          fontSize: 36,
          fontWeight: 700,
          color: '#FFFFFF',
          fontFamily: 'Arial, sans-serif',
          textTransform: 'uppercase',
          letterSpacing: 8,
          marginTop: 20,
          textAlign: 'center',
        }}
      >
        LUGARES ASOMBROSOS
      </div>

      {/* DEL MUNDO */}
      <div
        style={{
          opacity: subtitleOpacity,
          fontSize: 28,
          fontWeight: 300,
          color: 'rgba(255,255,255,0.7)',
          fontFamily: 'Arial, sans-serif',
          textTransform: 'uppercase',
          letterSpacing: 6,
          marginTop: 8,
          textAlign: 'center',
        }}
      >
        DEL MUNDO
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Verificar tipos**

```powershell
npm run typecheck
```

Resultado esperado: sin errores.

- [ ] **Step 3: Commit**

```powershell
git add src/Intro.tsx
git commit -m "feat: add Intro scene"
```

---

## Task 5: Outro.tsx — escena de cierre

**Files:**
- Create: `src/Outro.tsx`

**Interfaces:**
- Consumes: nada externo
- Produces: `Outro` — sin props, dura 150 frames internamente

- [ ] **Step 1: Crear `src/Outro.tsx`**

```tsx
import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';

export const Outro: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 40], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const ctaOpacity = interpolate(frame, [50, 90], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const outerOpacity = interpolate(frame, [120, 150], [1, 0], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: '#000',
        opacity: outerOpacity,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 24,
      }}
    >
      <div
        style={{
          opacity: titleOpacity,
          fontSize: 56,
          fontWeight: 700,
          color: '#FFFFFF',
          fontFamily: 'Arial, sans-serif',
          textAlign: 'center',
          letterSpacing: 2,
          padding: '0 60px',
        }}
      >
        ¿Cuál visitarías?
      </div>

      <div
        style={{
          opacity: ctaOpacity,
          fontSize: 44,
          fontWeight: 400,
          color: '#FFD700',
          fontFamily: 'Arial, sans-serif',
        }}
      >
        Comenta 👇
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Verificar tipos**

```powershell
npm run typecheck
```

Resultado esperado: sin errores.

- [ ] **Step 3: Commit**

```powershell
git add src/Outro.tsx
git commit -m "feat: add Outro scene"
```

---

## Task 6: TopPlaces.tsx — composición principal

**Files:**
- Modify: `src/TopPlaces.tsx` (reemplazar el placeholder del Task 2)

**Interfaces:**
- Consumes: `Intro`, `PlaceScene`, `Outro` de sus respectivos archivos
- Produces: `TopPlaces` — composición completa de 1800 frames con audio

- [ ] **Step 1: Reemplazar `src/TopPlaces.tsx` con la versión completa**

```tsx
import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { Intro } from './Intro';
import { Outro } from './Outro';
import { PlaceScene } from './PlaceScene';

const PLACES = [
  {
    rank: 5,
    name: 'Gran Cañón',
    location: 'Colorado, USA',
    fact: 'Tiene 446 km de largo y hasta 1,800 metros de profundidad',
    imageUrl:
      'https://images.unsplash.com/photo-1474044159687-1ee9f3a51722?w=1080&h=1920&fit=crop&q=80',
  },
  {
    rank: 4,
    name: 'Las Maldivas',
    location: 'Océano Índico',
    fact: 'Es el país más bajo del mundo, a solo 1.5 metros sobre el nivel del mar',
    imageUrl:
      'https://images.unsplash.com/photo-1512100356356-de1b84283e18?w=1080&h=1920&fit=crop&q=80',
  },
  {
    rank: 3,
    name: 'Aurora Boreal',
    location: 'Islandia',
    fact: 'Solo visible entre septiembre y marzo en zonas de oscuridad total',
    imageUrl:
      'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=1080&h=1920&fit=crop&q=80',
  },
  {
    rank: 2,
    name: 'Machu Picchu',
    location: 'Perú',
    fact: 'Construida en el siglo XV a 2,430 metros de altitud sobre el nivel del mar',
    imageUrl:
      'https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=1080&h=1920&fit=crop&q=80',
  },
  {
    rank: 1,
    name: 'Cueva Waitomo',
    location: 'Nueva Zelanda',
    fact: 'Miles de luciérnagas bioluminiscentes crean una galaxia natural bajo tierra',
    imageUrl:
      'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1080&h=1920&fit=crop&q=80',
  },
] as const;

export const TopPlaces: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      {/* Audio de fondo — coloca tu music.mp3 en la carpeta public/ */}
      <Audio src={staticFile('music.mp3')} volume={0.7} />

      {/* Intro: frames 0–150 (5 seg) */}
      <Sequence from={0} durationInFrames={150}>
        <Intro />
      </Sequence>

      {/* Lugares: frames 150–1650 (50 seg, 10 seg cada uno) */}
      {PLACES.map((place, i) => (
        <Sequence
          key={place.rank}
          from={150 + i * 300}
          durationInFrames={300}
        >
          <PlaceScene {...place} />
        </Sequence>
      ))}

      {/* Outro: frames 1650–1800 (5 seg) */}
      <Sequence from={1650} durationInFrames={150}>
        <Outro />
      </Sequence>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Verificar tipos**

```powershell
npm run typecheck
```

Resultado esperado: sin errores.

- [ ] **Step 3: Commit**

```powershell
git add src/TopPlaces.tsx
git commit -m "feat: complete TopPlaces composition with all scenes and audio"
```

---

## Task 7: Música, preview y renderizado final

**Files:**
- Acción manual: copiar `music.mp3` a `public/`

**Interfaces:**
- Consumes: todo el proyecto completo
- Produces: `out/video.mp4` — video final listo para subir

- [ ] **Step 1: Copiar tu archivo de música**

Copia tu archivo `.mp3` a la carpeta `public/` y renómbralo exactamente como `music.mp3`.

```
pronado remotion/
  public/
    music.mp3   ← aquí
```

> Si no tienes música aún, puedes continuar con el preview — Remotion mostrará un error de audio en la consola pero el video visual funcionará igual. Para el render final sí necesitas el archivo.

- [ ] **Step 2: Abrir el preview interactivo**

```powershell
npm start
```

Se abrirá el navegador en `http://localhost:3000`. Verifica:
- [ ] El video dura 60 segundos (1800 frames en el timeline)
- [ ] La intro "TOP 5" aparece con animación spring
- [ ] Cada lugar tiene imagen de fondo con zoom Ken Burns
- [ ] Los textos aparecen en secuencia (número → nombre → ubicación → dato)
- [ ] El outro muestra "¿Cuál visitarías?"
- [ ] La música suena (si pusiste el archivo)

- [ ] **Step 3: Test de frame único para verificar render**

```powershell
npx remotion render src/Root.tsx TopPlaces --frames=150 out/test-frame.png
```

Debe generar `out/test-frame.png` mostrando el inicio de la primera PlaceScene (Gran Cañón).

- [ ] **Step 4: Render del video completo**

```powershell
npm run build
```

Este proceso puede tardar varios minutos dependiendo de tu PC. El resultado es `out/video.mp4`.

- [ ] **Step 5: Commit final**

```powershell
git add -A
git commit -m "feat: complete TOP 5 video - ready to render"
```

---

## Notas de personalización post-render

- **Cambiar un lugar:** Edita el array `PLACES` en `src/TopPlaces.tsx` — cambia `name`, `location`, `fact` e `imageUrl`
- **Cambiar imagen:** Reemplaza la URL de Unsplash. Formato: `https://images.unsplash.com/photo-{ID}?w=1080&h=1920&fit=crop&q=80`
- **Cambiar volumen de música:** Modifica `volume={0.7}` en `<Audio>` (rango 0–1)
- **Cambiar velocidad Ken Burns:** En `PlaceScene.tsx` línea con `interpolate(frame, [0, 300], [1, 1.15]...)` — el `1.15` controla cuánto zoom. Más alto = más dramático.
