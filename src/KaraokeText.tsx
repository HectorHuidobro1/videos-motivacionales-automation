import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

export interface WordTiming {
  word: string;
  start: number;
  end: number;
}

export interface Sentence {
  start: number;
  end: number;
  words: WordTiming[];
}

export const KaraokeText: React.FC<{ sentence: Sentence }> = ({ sentence }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const startFrame = sentence.start * fps;
  const endFrame = sentence.end * fps;

  const opacity = interpolate(
    frame,
    [startFrame, startFrame + 6, endFrame - 6, endFrame],
    [0, 1, 1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  if (opacity === 0) return null;

  return (
    <div
      style={{
        opacity,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        alignContent: 'center',
        gap: '10px 16px',
        maxWidth: 900,
        padding: '0 60px',
      }}
    >
      {sentence.words.map((w, i) => {
        const wordStartFrame = w.start * fps;
        const wordEndFrame = w.end * fps;
        const isActive = frame >= wordStartFrame && frame < wordEndFrame;
        const isSpoken = frame >= wordEndFrame;

        const scale = interpolate(
          frame,
          [wordStartFrame, wordStartFrame + 3],
          [1, 1.14],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        ) * (isSpoken ? 1 / 1.14 : 1);

        const color = isActive
          ? '#FFD34D'
          : isSpoken
          ? '#FFFFFF'
          : 'rgba(255, 255, 255, 0.38)';

        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              transform: `scale(${scale})`,
              color,
              fontSize: 58,
              fontWeight: 600,
              fontFamily: 'Georgia, serif',
              fontStyle: 'italic',
              lineHeight: 1.3,
            }}
          >
            {w.word}
          </span>
        );
      })}
    </div>
  );
};
