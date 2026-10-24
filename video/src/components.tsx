import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, FONT} from './theme';
import {prog} from './utils';

const STAGES = 8;

/** Her sahnenin ortak iskeleti: başlık, aşama göstergesi, giriş/çıkış solması. */
export const Shell: React.FC<{
  stage?: number;
  stageName?: string;
  title: string;
  sub?: string;
  children: React.ReactNode;
}> = ({stage, stageName, title, sub, children}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const inA = prog(frame, 0, 10, Easing.linear);
  const outA = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const t = prog(frame, 0, 24);
  return (
    <AbsoluteFill style={{fontFamily: FONT, color: C.ink, opacity: inA * outA}}>
      {stage !== undefined && (
        <div style={{position: 'absolute', left: 96, top: 44, display: 'flex', alignItems: 'center', gap: 28}}>
          <div
            style={{
              fontSize: 28,
              fontWeight: 700,
              color: C.blue,
              background: C.blueTint,
              borderRadius: 999,
              padding: '8px 22px',
            }}
          >
            Aşama {stage}/{STAGES} · {stageName}
          </div>
          <div style={{display: 'flex', gap: 8}}>
            {Array.from({length: STAGES}).map((_, i) => (
              <div
                key={i}
                style={{
                  width: 52,
                  height: 10,
                  borderRadius: 5,
                  background: i < stage ? C.blue : C.grid,
                }}
              />
            ))}
          </div>
        </div>
      )}
      <div
        style={{
          position: 'absolute',
          left: 96,
          top: 112,
          opacity: t,
          transform: `translateY(${(1 - t) * 24}px)`,
        }}
      >
        <div style={{fontSize: 68, fontWeight: 800, letterSpacing: -1.5, lineHeight: 1.05}}>{title}</div>
        {sub && <div style={{fontSize: 32, color: C.muted, marginTop: 10, fontWeight: 500}}>{sub}</div>}
      </div>
      {children}
    </AbsoluteFill>
  );
};

/** Yay efektiyle beliren kutu (aşağıdan kayar). */
export const Pop: React.FC<{
  delay: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
  dy?: number;
  dx?: number;
}> = ({delay, style, children, dy = 30, dx = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: 28});
  return (
    <div
      style={{
        ...style,
        opacity: s,
        transform: `translate(${(1 - s) * dx}px, ${(1 - s) * dy}px)`,
      }}
    >
      {children}
    </div>
  );
};

export const Card: React.FC<{style?: React.CSSProperties; children?: React.ReactNode}> = ({style, children}) => (
  <div
    style={{
      background: C.card,
      border: `2px solid ${C.grid}`,
      borderRadius: 24,
      boxShadow: '0 8px 30px rgba(11,11,11,0.05)',
      ...style,
    }}
  >
    {children}
  </div>
);
