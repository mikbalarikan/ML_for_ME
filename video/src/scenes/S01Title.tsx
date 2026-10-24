import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {Pop} from '../components';
import {C, FONT} from '../theme';
import {prog} from '../utils';

const STEPS = ['Veriyi tanı', 'Etiketle', 'Ölçekle', 'Pencerele', 'Modeli kur', 'Eğit', 'Test et', 'Raporla'];

const Fan: React.FC<{cx: number; cy: number; r: number; frame: number}> = ({cx, cy, r, frame}) => {
  const blades = 22;
  const rot = frame * 5;
  return (
    <g transform={`translate(${cx} ${cy})`}>
      {[0, 1, 2].map((k) => {
        const p = ((frame + k * 30) % 90) / 90;
        return <circle key={k} r={r * (0.9 + p * 0.55)} fill="none" stroke={C.orange} strokeWidth={4} opacity={(1 - p) * 0.5} />;
      })}
      <circle r={r} fill={C.card} stroke={C.ink} strokeWidth={12} />
      <circle r={r - 26} fill={C.blueTint} stroke={C.blue} strokeWidth={3} />
      <g transform={`rotate(${rot})`}>
        {Array.from({length: blades}).map((_, i) => (
          <g key={i} transform={`rotate(${(i * 360) / blades})`}>
            <ellipse cx={0} cy={-r * 0.55} rx={r * 0.075} ry={r * 0.4} fill={C.blue} opacity={0.78} transform={`rotate(14 0 ${-r * 0.55})`} />
          </g>
        ))}
      </g>
      <circle r={r * 0.2} fill={C.ink} />
      <circle r={r * 0.09} fill={C.orange} />
    </g>
  );
};

export const S01Title: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const out = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {extrapolateLeft: 'clamp'});
  const fan = prog(frame, 0, 40);
  return (
    <AbsoluteFill style={{fontFamily: FONT, color: C.ink, opacity: out}}>
      <svg width={1920} height={1080} style={{position: 'absolute', opacity: fan, transform: `scale(${0.9 + 0.1 * fan})`, transformOrigin: '1440px 480px'}}>
        <Fan cx={1440} cy={480} r={330} frame={frame} />
      </svg>
      <Pop delay={4} style={{position: 'absolute', left: 96, top: 250, fontSize: 32, fontWeight: 700, color: C.orange, letterSpacing: 2}}>
        ML_for_ME · KESTİRİMCİ BAKIM
      </Pop>
      <Pop delay={10} style={{position: 'absolute', left: 96, top: 310, fontSize: 124, fontWeight: 800, letterSpacing: -3, lineHeight: 1.02}}>
        Turbofan Motoru
        <br />
        Arıza Tahmini
      </Pop>
      <Pop delay={24} style={{position: 'absolute', left: 100, top: 590, fontSize: 52, fontWeight: 500, color: C.muted}}>
        8 adımda uygulamalı makine öğrenmesi
      </Pop>
      <div style={{position: 'absolute', left: 96, top: 860, display: 'flex', gap: 14}}>
        {STEPS.map((s, i) => {
          const a = prog(frame, 44 + i * 5, 18);
          return (
            <div
              key={s}
              style={{
                opacity: a,
                transform: `translateY(${(1 - a) * 20}px)`,
                background: C.card,
                border: `2px solid ${C.grid}`,
                borderRadius: 16,
                padding: '12px 18px',
                fontSize: 26,
                fontWeight: 600,
                whiteSpace: 'nowrap',
              }}
            >
              <span style={{color: C.blue, marginRight: 8}}>{i + 1}</span>
              {s}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
