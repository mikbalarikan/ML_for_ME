import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Pop, Shell} from '../components';
import data from '../data/data.json';
import {C} from '../theme';
import {prog} from '../utils';

const MX = 250, MY = 440, CW = 290, CH = 200;
const BX = 1040, BW = 560;

export const S09Test: React.FC = () => {
  const frame = useCurrentFrame();
  const a = data.test.at05;
  const cnt = prog(frame, 80, 60);
  const cells = [
    {k: 'TN', v: a.tn, x: 0, y: 0, c: C.green, tint: C.greenTint, t: 'doğru: sağlam'},
    {k: 'FP', v: a.fp, x: 1, y: 0, c: C.red, tint: C.redTint, t: 'boş alarm'},
    {k: 'FN', v: a.fn, x: 0, y: 1, c: C.red, tint: C.redTint, t: 'kaçırılan arıza'},
    {k: 'TP', v: a.tp, x: 1, y: 1, c: C.blue, tint: C.blueTint, t: 'yakalanan arıza'},
  ];
  // 93 nokta: TN, FP, FN, TP sırasıyla
  const dots: string[] = [
    ...Array(a.tn).fill(C.green), ...Array(a.fp).fill(C.red), ...Array(a.fn).fill(C.red), ...Array(a.tp).fill(C.blue),
  ];
  const colorize = prog(frame, 50, 20);
  const metrics = [
    {n: 'accuracy', v: a.acc, c: C.blue},
    {n: 'precision', v: a.prec, c: C.green},
    {n: 'recall', v: a.rec, c: C.orange},
    {n: 'F1', v: a.f1, c: C.blue},
  ];
  const lr = data.test.logreg.rec;
  return (
    <Shell stage={7} stageName="Test et" title="Test et" sub="Eğitimde hiç görülmemiş 93 motor · her motorun son 50 çevrimi">
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {dots.map((c, i) => {
          const ap = prog(frame, 6 + i * 0.35, 12);
          return <circle key={i} cx={104 + i * 18.7} cy={310} r={7.5 * ap} fill={colorize > 0.5 ? c : C.faint} opacity={0.95} />;
        })}
        <text x={96} y={362} fontSize={24} fill={C.muted} fontWeight={600} opacity={colorize}>
          <tspan fill={C.green}>● 68 sağlam doğru</tspan>   <tspan fill={C.red}>● 4 kaçırılan</tspan>   <tspan fill={C.blue}>● 21 yakalanan</tspan>
        </text>
      </svg>
      <div style={{position: 'absolute', left: MX - 150, top: MY - 90, width: CW * 2 + 160, fontSize: 28, fontWeight: 700, color: C.muted}}>
        <div style={{position: 'absolute', left: 150, width: CW, textAlign: 'center', top: 28}}>model: sağlam</div>
        <div style={{position: 'absolute', left: 150 + CW, width: CW, textAlign: 'center', top: 28}}>model: tehlike</div>
      </div>
      <div style={{position: 'absolute', left: 96, top: MY, width: 150, height: CH, display: 'flex', alignItems: 'center', fontSize: 28, fontWeight: 700, color: C.muted, lineHeight: 1.15}}>gerçek:<br />sağlam</div>
      <div style={{position: 'absolute', left: 96, top: MY + CH, width: 150, height: CH, display: 'flex', alignItems: 'center', fontSize: 28, fontWeight: 700, color: C.muted, lineHeight: 1.15}}>gerçek:<br />tehlike</div>
      {cells.map((c, i) => (
        <Pop key={c.k} delay={30 + i * 8} dy={20} style={{position: 'absolute', left: MX + c.x * CW, top: MY + c.y * CH, width: CW - 10, height: CH - 10}}>
          <div style={{background: c.v === 0 ? '#f4f3f0' : c.tint, border: `3px solid ${c.v === 0 ? C.grid : c.c}`, borderRadius: 22, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
            <div style={{fontSize: 84, fontWeight: 800, color: c.v === 0 ? C.faint : c.c, fontVariantNumeric: 'tabular-nums', lineHeight: 1}}>{Math.round(c.v * cnt)}</div>
            <div style={{fontSize: 28, fontWeight: 800, color: C.ink, marginTop: 8}}>{c.k}</div>
            <div style={{fontSize: 22, fontWeight: 600, color: C.muted}}>{c.t}</div>
          </div>
        </Pop>
      ))}

      {/* metrikler */}
      <div style={{position: 'absolute', left: BX, top: 410, fontSize: 30, fontWeight: 800}}>Metrikler (eşik 0.5)</div>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {metrics.map((m, i) => {
          const y = 490 + i * 100;
          const p = prog(frame, 100 + i * 12, 50);
          return (
            <g key={m.n}>
              <text x={BX} y={y + 6} fontSize={30} fontWeight={700} fill={C.ink}>{m.n}</text>
              <rect x={BX + 200} y={y - 22} width={BW - 120} height={36} rx={12} fill={C.grid} opacity={0.6} />
              <rect x={BX + 200} y={y - 22} width={(BW - 120) * m.v * p} height={36} rx={12} fill={m.c} />
              <text x={BX + 200 + BW - 120 + 22} y={y + 8} fontSize={36} fontWeight={800} fill={m.c} style={{fontVariantNumeric: 'tabular-nums'}}>{(m.v * p).toFixed(3)}</text>
              {m.n === 'recall' && (
                <g opacity={prog(frame, 190, 20)}>
                  <line x1={BX + 200 + (BW - 120) * lr} x2={BX + 200 + (BW - 120) * lr} y1={y - 38} y2={y + 30} stroke={C.ink} strokeWidth={4} />
                  <text x={BX + 200 + (BW - 120) * lr} y={y - 52} fontSize={24} fontWeight={700} fill={C.ink} textAnchor="middle">lojistik regresyon 0.72</text>
                </g>
              )}
            </g>
          );
        })}
      </svg>
      <Pop delay={215} style={{position: 'absolute', left: BX, top: 910, width: 800, fontSize: 28, lineHeight: 1.35, color: C.muted, fontWeight: 500}}>
        <b style={{color: C.green}}>FP = 0</b>: “tehlike” dediyse gerçekten tehlike. Ama <b style={{color: C.red}}>4 arıza kaçırıldı</b>; LSTM, klasik modelden iyi: recall 0.72 → 0.84.
      </Pop>
    </Shell>
  );
};
