import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Pop, Shell} from '../components';
import data from '../data/data.json';
import {C, MONO} from '../theme';
import {easeIO, fmtInt, lerp, partial, prog, toPath, Pt} from '../utils';

const X0 = 190, X1 = 1250, Y0 = 400, Y1 = 700;

export const S04Etiket: React.FC = () => {
  const frame = useCurrentFrame();
  const e1 = data.engine1;
  const N = e1.cycles; // 192
  const p = prog(frame, 20, 140, easeIO);
  const c = Math.max(1, Math.min(N, Math.round(1 + p * (N - 1)))); // şu anki çevrim
  const rul = e1.rul[c - 1];
  const lab = e1.label[c - 1];
  const pts: Pt[] = e1.rul.map((v, i) => [lerp(X0, X1, i / (N - 1)), lerp(Y1, Y0, v / (N - 1))]);
  const drawn = partial(pts, (c - 1) / (N - 1));
  const last = drawn[drawn.length - 1];
  const yThr = lerp(Y1, Y0, 30 / (N - 1));
  const xFlip = lerp(X0, X1, (e1.firstLabel1Cycle - 1) / (N - 1));
  const bars = prog(frame, 150, 50);
  const cb = data.classBalance;
  const tot = cb.safe + cb.danger;
  const BH = 260;
  return (
    <Shell stage={2} stageName="Etiketle" title="Etiketle" sub="Doğru cevap dosyada yok; arıza anından geriye sayarak biz üretiyoruz">
      {/* formül */}
      <div style={{position: 'absolute', left: 96, top: 262, fontSize: 40, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 18, whiteSpace: 'nowrap'}}>
        <span style={{color: C.muted}}>Motor 1</span>
        <span>RUL = son çevrim − çevrim =</span>
        <span style={{fontFamily: MONO, fontSize: 38}}>{N} − {c} =</span>
        <span style={{color: lab ? C.orange : C.blue, fontSize: 52, minWidth: 80, fontVariantNumeric: 'tabular-nums'}}>{rul}</span>
        <span style={{color: C.muted}}>→ etiket</span>
        <span
          style={{
            background: lab ? C.orange : C.blue,
            color: '#fff',
            borderRadius: 14,
            padding: '2px 22px',
            fontSize: 48,
            fontWeight: 800,
          }}
        >
          {lab}
        </span>
      </div>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {/* eşik bölgesi */}
        <rect x={X0} y={yThr} width={X1 - X0} height={Y1 - yThr} fill={C.orange} opacity={0.1} />
        <line x1={X0} x2={X1} y1={yThr} y2={yThr} stroke={C.orange} strokeWidth={3} strokeDasharray="10 8" />
        <text x={X0 + 10} y={yThr - 12} fontSize={26} fontWeight={700} fill={C.orange}>RUL ≤ 30 → etiket 1</text>
        <line x1={X0} x2={X0} y1={Y0} y2={Y1} stroke={C.faint} strokeWidth={2} />
        <line x1={X0} x2={X1} y1={Y1} y2={Y1} stroke={C.faint} strokeWidth={2} />
        {[0, 50, 100, 150].map((v) => (
          <text key={v} x={X0 - 14} y={lerp(Y1, Y0, v / (N - 1)) + 9} fontSize={24} fill={C.faint} textAnchor="end">{v}</text>
        ))}
        {[1, 50, 100, 150, 192].map((v) => (
          <text key={v} x={lerp(X0, X1, (v - 1) / (N - 1))} y={Y1 + 36} fontSize={24} fill={C.faint} textAnchor="middle">{v}</text>
        ))}
        <text x={X0 - 70} y={Y0 - 16} fontSize={26} fill={C.muted} fontWeight={600}>RUL (kalan ömür, çevrim)</text>
        <text x={(X0 + X1) / 2} y={Y1 + 80} fontSize={26} fill={C.muted} textAnchor="middle" fontWeight={600}>çevrim (192. çevrimde arıza)</text>
        <path d={toPath(partial(pts, Math.min(c - 1, e1.firstLabel1Cycle - 1) / (N - 1)))} fill="none" stroke={C.blue} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
        {c >= e1.firstLabel1Cycle && (
          <path d={toPath(drawn.filter((_, i) => i >= e1.firstLabel1Cycle - 2))} fill="none" stroke={C.orange} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
        )}
        <circle cx={last[0]} cy={last[1]} r={12} fill={lab ? C.orange : C.blue} />
        {/* etiket şeridi */}
        {e1.label.map((l, i) => {
          if (i >= c) return null;
          const w = (X1 - X0) / N;
          return <rect key={i} x={X0 + i * w} y={Y1 + 110} width={w + 0.5} height={40} fill={l ? C.orange : C.blue} opacity={0.9} />;
        })}
        <rect x={X0} y={Y1 + 110} width={X1 - X0} height={40} fill="none" stroke={C.grid} strokeWidth={2} />
        <text x={X0} y={Y1 + 186} fontSize={26} fill={C.muted} fontWeight={600}>etiket şeridi: <tspan fill={C.blue}>0 güvenli</tspan> · <tspan fill={C.orange}>1 tehlike</tspan></text>
        {c >= e1.firstLabel1Cycle && (
          <g>
            <line x1={xFlip} x2={xFlip} y1={Y1 + 100} y2={Y1 + 162} stroke={C.ink} strokeWidth={3} />
            <line x1={xFlip} x2={xFlip} y1={Y0 + 40} y2={yThr} stroke={C.orange} strokeWidth={3} strokeDasharray="4 6" />
            <text x={xFlip} y={Y0 + 28} fontSize={28} fontWeight={800} textAnchor="middle" fill={C.orange}>çevrim {e1.firstLabel1Cycle}: etiket 0 → 1</text>
          </g>
        )}
      </svg>

      {/* sınıf dengesi */}
      <div style={{position: 'absolute', left: 1400, top: 334, fontSize: 30, fontWeight: 700}}>Sınıf dengesi (20.631 satır)</div>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {[
          {v: cb.safe, c: C.blue, x: 1420, t: '0 · güvenli', pct: '%85'},
          {v: cb.danger, c: C.orange, x: 1630, t: '1 · tehlike', pct: '%15'},
        ].map((b) => {
          const h = (b.v / tot) * BH * 1.0 * bars;
          return (
            <g key={b.t}>
              <rect x={b.x} y={720 - h} width={150} height={h} rx={10} fill={b.c} />
              <text x={b.x + 75} y={720 - h - 54} fontSize={46} fontWeight={800} textAnchor="middle" fill={b.c} opacity={bars}>{b.pct}</text>
              <text x={b.x + 75} y={720 - h - 18} fontSize={26} fontWeight={600} textAnchor="middle" fill={C.muted} opacity={bars}>{fmtInt(b.v * bars)}</text>
              <text x={b.x + 75} y={766} fontSize={26} fontWeight={700} textAnchor="middle" fill={C.ink}>{b.t}</text>
            </g>
          );
        })}
        <line x1={1400} x2={1810} y1={720} y2={720} stroke={C.faint} strokeWidth={2} />
      </svg>
      <Pop delay={190} style={{position: 'absolute', left: 1400, top: 800, width: 430, fontSize: 28, lineHeight: 1.35, color: C.muted, fontWeight: 500}}>
        Hep “0” diyen tembel model bile <b style={{color: C.red}}>%85 doğru</b> çıkar. Accuracy tek başına yeterli değil.
      </Pop>
    </Shell>
  );
};
