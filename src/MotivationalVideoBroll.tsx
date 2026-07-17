import React from 'react';
import {
  AbsoluteFill,
  Video,
  Audio,
  Sequence,
  Loop,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from 'remotion';
import captions from './captions_karaoke.json';
import clipsRaw from './clips.json';
import { KaraokeText, Sentence } from './KaraokeText';

interface Clip {
  file: string;
  durationInFrames: number;
}

const sentences: Sentence[] = captions;
const clips: Clip[] = clipsRaw;

export const MotivationalVideoBroll: React.FC = () => {
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
    <AbsoluteFill style={{ background: '#000', opacity: outerOpacity }}>
      <Audio src={staticFile('voice.mp3')} volume={1} />

      {sentences.map((s, i) => {
        const clip = clips[i];
        const startFrame = Math.round(s.start * fps);
        const endFrame = Math.round(s.end * fps);
        const sentenceDuration = Math.max(endFrame - startFrame, 1);

        if (!clip) return null;

        return (
          <Sequence key={i} from={startFrame} durationInFrames={sentenceDuration}>
            <AbsoluteFill>
              {/* Video (no OffthreadVideo): OffthreadVideo's frame-accurate
                  extraction hit intermittent "no frame found" errors on Windows
                  during full renders, even with 30fps/short-GOP re-encoded clips. */}
              <Loop durationInFrames={clip.durationInFrames}>
                <Video
                  src={staticFile(`clips/${clip.file}`)}
                  muted
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                />
              </Loop>
              <AbsoluteFill style={{ background: 'rgba(0,0,0,0.45)' }} />
            </AbsoluteFill>
          </Sequence>
        );
      })}

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
