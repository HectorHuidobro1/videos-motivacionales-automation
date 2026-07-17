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
