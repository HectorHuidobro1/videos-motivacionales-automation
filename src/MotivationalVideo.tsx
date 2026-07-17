import React from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from 'remotion';
import captions from './captions.json';

interface Segment {
  start: number;
  end: number;
  text: string;
}

const segments: Segment[] = captions;

const CaptionText: React.FC<{ segment: Segment }> = ({ segment }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const startFrame = segment.start * fps;
  const endFrame = segment.end * fps;
  const duration = Math.max(endFrame - startFrame, 1);
  // Frases cortas duran poco en pantalla: el fade debe ser breve para no comerse
  // la mayor parte del tiempo visible de la frase.
  const fade = Math.min(3, Math.floor(duration / 3));

  const opacity = interpolate(
    frame,
    [startFrame, startFrame + fade, endFrame - fade, endFrame],
    [0, 1, 1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const scale = interpolate(frame, [startFrame, startFrame + fade], [0.9, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  if (opacity === 0) return null;

  return (
    <div
      style={{
        opacity,
        transform: `scale(${scale})`,
        fontSize: 64,
        fontWeight: 500,
        color: '#FFFFFF',
        fontFamily: 'Georgia, serif',
        fontStyle: 'italic',
        textAlign: 'center',
        lineHeight: 1.3,
        maxWidth: 900,
        padding: '0 60px',
      }}
    >
      {segment.text}
    </div>
  );
};

export const MotivationalVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const fadeOut = interpolate(
    frame,
    [durationInFrames - fps * 1.5, durationInFrames],
    [1, 0],
    { extrapolateLeft: 'clamp' }
  );
  const outerOpacity = Math.min(fadeIn, fadeOut);

  return (
    <AbsoluteFill
      style={{
        background: '#000',
        opacity: outerOpacity,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Audio src={staticFile('voice.mp3')} volume={1} />

      {segments.map((seg, i) => (
        <AbsoluteFill
          key={i}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <CaptionText segment={seg} />
        </AbsoluteFill>
      ))}
    </AbsoluteFill>
  );
};
