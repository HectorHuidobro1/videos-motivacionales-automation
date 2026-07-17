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

  const scale = interpolate(frame, [0, 300], [1, 1.15], {
    extrapolateRight: 'clamp',
  });

  const opacity = interpolate(frame, [0, 30, 270, 300], [0, 1, 1, 0], {
    extrapolateRight: 'clamp',
  });

  const rankProgress = spring({
    frame: frame - 30,
    fps,
    config: { damping: 12, stiffness: 100 },
  });
  const rankY = interpolate(rankProgress, [0, 1], [80, 0]);
  const rankOpacity = interpolate(frame, [30, 60], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const nameOpacity = interpolate(frame, [60, 90], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const nameY = interpolate(frame, [60, 90], [20, 0], {
    extrapolateRight: 'clamp',
  });

  const locationOpacity = interpolate(frame, [120, 150], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const factOpacity = interpolate(frame, [180, 210], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill>
        <Img
          src={imageUrl}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${scale})`,
            transformOrigin: 'center center',
            translate: "101.7px -232.9px"
          }}
          from={-2} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: 'rgba(0,0,0,0.45)' }} />
      <AbsoluteFill
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '0 60px',
        }}
      >
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
