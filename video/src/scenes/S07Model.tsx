import React from 'react';
import {Img, staticFile, useCurrentFrame, useVideoConfig, spring} from 'remotion';
import {Card, Pop, Shell} from '../components';
import {C, MONO} from '../theme';
import {fmtInt, prog} from '../utils';

const LAYERS = [
  {name: 'Girdi', detail: '(50, 15)', params: 0, h: 150, color: C.faint, note: '50 çevrim × 15 özellik'},
  {name: 'LSTM 100', detail: '(50, 100)', params: 46400, h: 230, color: C.blue, note: 'her çevrimde hafıza'},
  {name: 'Dropout', detail: '%20', params: 0, h: 130, color: C.orange, note: 'ezberi önler'},
  {name: 'LSTM 50', detail: '(50)', params: 30200, h: 180, color: C.blue, note: 'son hafıza'},
  {name: 'Dropout', detail: '%20', params: 0, h: 130, color: C.orange, note: 'ezberi önler'},
  {name: 'Dense 1', detail: 'sigmoid', params: 51, h: 110, color: C.green, note: 'arıza olasılığı'},
];
const BW = 232, GAP = 62, X0 = 96, CY = 400;

export const S07Model: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  let total = 0;
  const sp = LAYERS.map((_, i) => spring({frame: frame - (10 + i * 20), fps, config: {damping: 200}, durationInFrames: 26}));
  LAYERS.forEach((l, i) => (total += l.params * sp[i]));
  const heat = prog(frame, 170, 30);
  const form = prog(frame, 140, 24);
  return (
    <Shell stage={5} stageName="Modeli kur" title="Modeli kur" sub="LSTM: veriyi zaman sırasıyla okuyan, hafızası olan sinir ağı">
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {LAYERS.map((l, i) => {
          if (i === LAYERS.length - 1) return null;
          const x = X0 + (i + 1) * BW + i * GAP;
          const a = Math.min(sp[i], sp[i + 1]);
          return (
            <g key={i} opacity={a}>
              <line x1={x + 8} x2={x + GAP - 14} y1={CY} y2={CY} stroke={C.muted} strokeWidth={4} />
              <path d={`M${x + GAP - 22} ${CY - 11} L${x + GAP - 8} ${CY} L${x + GAP - 22} ${CY + 11}`} fill="none" stroke={C.muted} strokeWidth={4} />
            </g>
          );
        })}
      </svg>
      {LAYERS.map((l, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: X0 + i * (BW + GAP),
            top: CY - l.h / 2,
            width: BW,
            height: l.h,
            opacity: sp[i],
            transform: `translateY(${(1 - sp[i]) * 50}px) scale(${0.9 + 0.1 * sp[i]})`,
            background: l.color === C.faint ? '#f0efec' : l.color,
            color: l.color === C.faint ? C.ink : '#fff',
            borderRadius: 22,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 10px 28px rgba(11,11,11,0.12)',
          }}
        >
          <div style={{fontSize: 36, fontWeight: 800}}>{l.name}</div>
          <div style={{fontSize: 30, fontWeight: 600, fontFamily: MONO, marginTop: 6, opacity: 0.92}}>{l.detail}</div>
        </div>
      ))}
      {LAYERS.map((l, i) => (
        <div key={i} style={{position: 'absolute', left: X0 + i * (BW + GAP) - 10, top: CY + 128, width: BW + 20, textAlign: 'center', opacity: sp[i]}}>
          <div style={{fontSize: 24, color: C.muted, fontWeight: 600, lineHeight: 1.2}}>{l.note}</div>
          <div style={{fontSize: 28, fontWeight: 800, marginTop: 6, color: l.params ? C.ink : C.faint}}>{l.params ? `${fmtInt(l.params)} param.` : '0 param.'}</div>
        </div>
      ))}
      <div style={{position: 'absolute', left: 96, top: 610, fontSize: 30, color: C.muted, fontWeight: 600}}>
        Toplam <span style={{color: C.blue, fontSize: 56, fontWeight: 800, fontVariantNumeric: 'tabular-nums', margin: '0 10px'}}>{fmtInt(total)}</span> parametre
      </div>

      <Pop delay={140} style={{position: 'absolute', left: 96, top: 710, width: 800}}>
        <Card style={{padding: '24px 34px'}}>
          <div style={{fontSize: 28, fontWeight: 700, color: C.muted}}>LSTM hücresinin fikri</div>
          <div style={{fontFamily: MONO, fontSize: 52, fontWeight: 800, margin: '14px 0 10px', whiteSpace: 'nowrap'}}>
            c<sub style={{fontSize: 28}}>t</sub> = <span style={{color: C.orange}}>f</span> · c<sub style={{fontSize: 28}}>t−1</sub> + <span style={{color: C.blue}}>i</span> · <span style={{color: C.green}}>g</span>
          </div>
          <div style={{fontSize: 27, color: C.muted, lineHeight: 1.35}}>
            <b style={{color: C.orange}}>f</b> unut kapısı · <b style={{color: C.blue}}>i</b> giriş kapısı · <b style={{color: C.green}}>g</b> yeni bilgi
          </div>
          <div style={{fontSize: 32, fontWeight: 800, marginTop: 10, opacity: form}}>≈ <span style={{color: C.orange}}>kendini ayarlayan filtre</span></div>
        </Card>
      </Pop>
      <div style={{position: 'absolute', left: 1000, top: 700, width: 824, opacity: heat, transform: `translateY(${(1 - heat) * 24}px)`}}>
        <Img src={staticFile('09_lstm_hafiza.png')} style={{width: 824, borderRadius: 16, border: `2px solid ${C.grid}`}} />
        <div style={{fontSize: 23, color: C.muted, fontWeight: 600, marginTop: 6}}>
          Hafıza haritası: arızaya yakın motorda son çevrimlerde keskin değişim
        </div>
      </div>
    </Shell>
  );
};
