import React from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from 'remotion';
import captions from './captions_karaoke.json';
import { KaraokeText, Sentence } from './KaraokeText';

const sentences: Sentence[] = captions;

export const MotivationalVideoKaraoke: React.FC = () => {
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

      {sentences.map((s, i) => (
        <AbsoluteFill
          key={i}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <KaraokeText sentence={s} />
        </AbsoluteFill>
      ))}
    </AbsoluteFill>
  );
};
