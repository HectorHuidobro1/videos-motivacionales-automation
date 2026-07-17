import React from 'react';
import { Composition, registerRoot } from 'remotion';
import { TopPlaces } from './TopPlaces';
import { MotivationalVideo } from './MotivationalVideo';
import { MotivationalVideoKaraoke } from './MotivationalVideoKaraoke';
import { MotivationalVideoBroll } from './MotivationalVideoBroll';
import captionsRaw from './captions.json';
import captionsKaraokeRaw from './captions_karaoke.json';

const captions = captionsRaw as { start: number; end: number; text: string }[];
const totalDuration = captions.length > 0
  ? Math.ceil((captions[captions.length - 1].end + 2) * 30)
  : 900;

const captionsKaraoke = captionsKaraokeRaw as { start: number; end: number }[];
const karaokeDuration = captionsKaraoke.length > 0
  ? Math.ceil((captionsKaraoke[captionsKaraoke.length - 1].end + 2) * 30)
  : 900;

const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="TopPlaces"
        component={TopPlaces}
        durationInFrames={1800}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="Motivacional"
        component={MotivationalVideo}
        durationInFrames={totalDuration}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="MotivacionalKaraoke"
        component={MotivationalVideoKaraoke}
        durationInFrames={karaokeDuration}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="MotivacionalBroll"
        component={MotivationalVideoBroll}
        durationInFrames={karaokeDuration}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};

registerRoot(RemotionRoot);
