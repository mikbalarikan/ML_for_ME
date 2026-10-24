import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Card, Pop, Shell} from '../components';
import data from '../data/data.json';
import {C} from '../theme';
import {easeIO, lerp, partial, prog, toPath, Pt} from '../utils';

const X0 = 140, X1 = 1780, Y0 = 400, Y1 = 660;

export const S02Problem: React.FC = () => {
  const frame = useCurrentFrame();
  const s11 = data.degradation.sensors.s11.norm; // 126 nokta: arızaya kalan 125 -> 0
  const n = s11.length;
  const pts: Pt[] = s11.map((v, i) => [lerp(X0, X1, i / (n - 1)), lerp(Y1, Y0, v)]);
  const t = prog(frame, 14, 100, easeIO);
  const drawn = partial(pts, t);
  const last = drawn[drawn.length - 1];
  const flight = Math.round(t * 125) + 0;
  const zoneX = lerp(X0, X1, (n - 1 - 30) / (n - 1));
  const zone = prog(frame, 96, 20);
  const health = 1 - t;
  return (
    <Shell title="Problem" sub="Motor her uçuşta (1 çevrim) biraz yıpranır; sensörler bunu fısıldar">
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {/* eksen */}
        <line x1={X0} y1={Y1 + 14} x2={X1} y2={Y1 + 14} stroke={C.grid} strokeWidth={3} />
        {Array.from({length: 6}).map((_, i) => {
          const x = lerp(X0, X1, i / 5);
          return <line key={i} x1={x} y1={Y1 + 14} x2={x} y2={Y1 + 26} stroke={C.faint} strokeWidth={2} />;
        })}
        <text x={X0} y={Y1 + 64} fontSize={28} fill={C.muted}>ilk uçuş</text>
        <text x={X1} y={Y1 + 64} fontSize={28} fill={C.muted} textAnchor="end">arıza</text>
        <text x={(X0 + X1) / 2 - 100} y={Y1 + 64} fontSize={28} fill={C.muted}>uçuş sayısı  →</text>
        {/* son 30 çevrim bölgesi */}
        <rect x={zoneX} y={Y0 - 30} width={(X1 - zoneX) * zone} height={Y1 - Y0 + 44} fill={C.orange} opacity={0.14} rx={10} />
        <text x={(zoneX + X1) / 2} y={Y0 - 44} fontSize={30} fontWeight={700} fill={C.orange} textAnchor="middle" opacity={zone}>
          son 30 çevrim
        </text>
        <path d={toPath(drawn)} fill="none" stroke={C.blue} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" />
        <circle cx={last[0]} cy={last[1]} r={13} fill={C.blue} />
        <circle cx={last[0]} cy={last[1]} r={26} fill={C.blue} opacity={0.2} />
        <text x={X0} y={Y0 + 6} fontSize={28} fill={C.muted} fontWeight={600}>sensör ölçümü (ortalama) ↑</text>
      </svg>
      {/* sağlık göstergesi */}
      <div style={{position: 'absolute', left: 1300, top: 262, width: 480, fontSize: 28, color: C.muted, fontWeight: 600}}>
        <div style={{display: 'flex', justifyContent: 'space-between'}}>
          <span>Motor sağlığı</span>
          <span style={{color: health > 0.5 ? C.green : health > 0.25 ? C.orange : C.red}}>{Math.round(health * 100)}%</span>
        </div>
        <div style={{height: 14, borderRadius: 7, background: C.grid, marginTop: 8, overflow: 'hidden'}}>
          <div style={{width: `${health * 100}%`, height: '100%', background: health > 0.5 ? C.green : health > 0.25 ? C.orange : C.red}} />
        </div>
      </div>
      <Pop delay={112} style={{position: 'absolute', left: 96, top: 790, width: 1728}}>
        <Card style={{padding: '30px 44px', borderColor: C.orange}}>
          <div style={{fontSize: 56, fontWeight: 800, letterSpacing: -1}}>
            Bu motor önümüzdeki <span style={{color: C.orange}}>30 uçuş</span> içinde arızalanır mı?
          </div>
        </Card>
      </Pop>
      <Pop delay={140} style={{position: 'absolute', left: 96, top: 955, fontSize: 34, color: C.muted, fontWeight: 500}}>
        <span style={{color: C.green, fontWeight: 800}}>Kestirimci bakım</span> (predictive maintenance): arızayı olmadan önce tahmin et, bakımı planla.
      </Pop>
      <div style={{position: 'absolute', left: 140, top: Y0 + 50, fontSize: 40, color: C.muted, fontWeight: 600}}>
        uçuş <span style={{color: C.ink, fontWeight: 800, fontVariantNumeric: 'tabular-nums'}}>{flight}</span>
      </div>
    </Shell>
  );
};
