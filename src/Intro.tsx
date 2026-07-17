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

  const top5Scale = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 80 },
  });
  const top5Opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const subtitleOpacity = interpolate(frame, [60, 100], [0, 1], {
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
      }}
    >
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
