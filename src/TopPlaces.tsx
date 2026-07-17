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
      <Audio src={staticFile('music.mp3')} volume={0.7} />

      <Sequence from={0} durationInFrames={150}>
        <Intro />
      </Sequence>

      {PLACES.map((place, i) => (
        <Sequence
          key={place.rank}
          from={150 + i * 300}
          durationInFrames={300}
        >
          <PlaceScene {...place} />
        </Sequence>
      ))}

      <Sequence from={1650} durationInFrames={150}>
        <Outro />
      </Sequence>
    </AbsoluteFill>
  );
};
