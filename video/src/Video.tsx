import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {C} from './theme';
import {S01Title} from './scenes/S01Title';
import {S02Problem} from './scenes/S02Problem';
import {S03Veri} from './scenes/S03Veri';
import {S04Etiket} from './scenes/S04Etiket';
import {S05Olcek} from './scenes/S05Olcek';
import {S06Pencere} from './scenes/S06Pencere';
import {S07Model} from './scenes/S07Model';
import {S08Egitim} from './scenes/S08Egitim';
import {S09Test} from './scenes/S09Test';
import {S10Esik} from './scenes/S10Esik';
import {S11Kapanis} from './scenes/S11Kapanis';

// [bileşen, süre (kare, 30 fps)]
export const SCENES: [React.FC, number][] = [
  [S01Title, 135], // 4.5 sn
  [S02Problem, 195], // 6.5
  [S03Veri, 270], // 9
  [S04Etiket, 240], // 8
  [S05Olcek, 180], // 6
  [S06Pencere, 270], // 9
  [S07Model, 300], // 10
  [S08Egitim, 300], // 10
  [S09Test, 300], // 10
  [S10Esik, 210], // 7
  [S11Kapanis, 180], // 6
];

export const STARTS = SCENES.reduce<number[]>((a, s, i) => [...a, i === 0 ? 0 : a[i - 1] + SCENES[i - 1][1]], []);
export const TOTAL = SCENES.reduce((a, s) => a + s[1], 0);

export const Video: React.FC = () => (
  <AbsoluteFill style={{background: C.bg}}>
    {SCENES.map(([Comp, dur], i) => (
      <Sequence key={i} from={STARTS[i]} durationInFrames={dur}>
        <Comp />
      </Sequence>
    ))}
  </AbsoluteFill>
);
