import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Card, Pop, Shell} from '../components';
import data from '../data/data.json';
import {C} from '../theme';
import {easeIO, fmtInt, lerp, partial, prog, toPath, Pt} from '../utils';

const DROP = [1, 5, 6, 10, 16, 18, 19];
const CX0 = 900, CX1 = 1800, CY0 = 470, CY1 = 800;
const LINES = [
  {k: 's4', name: 's4 · T50 sıcaklık', color: C.orange, arrow: '↑'},
  {k: 's11', name: 's11 · Ps30 basınç', color: C.blue, arrow: '↑'},
  {k: 's7', name: 's7 · P30 basınç', color: C.green, arrow: '↓'},
] as const;

const Stat: React.FC<{delay: number; y: number; to: number; label: string; color: string}> = ({delay, y, to, label, color}) => {
  const f = useCurrentFrame();
  const v = to * prog(f, delay + 4, 50);
  return (
    <Pop delay={delay} style={{position: 'absolute', left: 96, top: y, width: 600}}>
      <Card style={{padding: '12px 30px', display: 'flex', alignItems: 'baseline', gap: 22}}>
        <div style={{fontSize: 68, fontWeight: 800, color, minWidth: 200, fontVariantNumeric: 'tabular-nums'}}>{fmtInt(v)}</div>
        <div style={{fontSize: 34, fontWeight: 600, color: C.muted}}>{label}</div>
      </Card>
    </Pop>
  );
};

export const S03Veri: React.FC = () => {
  const frame = useCurrentFrame();
  const sens = data.degradation.sensors;
  const drop = prog(frame, 190, 30);
  const keep = prog(frame, 214, 20);
  return (
    <Shell stage={1} stageName="Veriyi tanı" title="Veriyi tanı" sub="NASA C-MAPSS: 100 motor, her biri arızaya kadar kaydedilmiş">
      <Stat delay={6} y={250} to={100} label="motor" color={C.blue} />
      <Stat delay={16} y={360} to={21} label="sensör" color={C.orange} />
      <Stat delay={26} y={470} to={20631} label="satır" color={C.green} />

      <div style={{position: 'absolute', left: 96, top: 612, fontSize: 28, fontWeight: 700, color: C.muted}}>21 sensör</div>
      <div style={{position: 'absolute', left: 96, top: 656, width: 600, display: 'flex', flexWrap: 'wrap', gap: 10}}>
        {Array.from({length: 21}).map((_, i) => {
          const n = i + 1;
          const isDrop = DROP.includes(n);
          const a = prog(frame, 40 + i * 2, 14);
          const col = isDrop ? lerp(0, 1, drop) : 0;
          return (
            <div
              key={n}
              style={{
                width: 76,
                height: 56,
                borderRadius: 14,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 26,
                fontWeight: 700,
                opacity: a * (1 - col * 0.7),
                transform: `scale(${0.7 + 0.3 * a - col * 0.1})`,
                background: isDrop && drop > 0.2 ? C.redTint : C.blueTint,
                color: isDrop && drop > 0.2 ? C.red : C.blue,
                textDecoration: isDrop && drop > 0.2 ? 'line-through' : 'none',
                border: `2px solid ${isDrop && drop > 0.2 ? C.red : 'transparent'}`,
              }}
            >
              s{n}
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 96, top: 888, width: 640, opacity: drop, fontSize: 30, lineHeight: 1.3, fontWeight: 600}}>
        <span style={{color: C.red}}>7 sabit sensör atılır</span>: bilgi taşımıyorlar
        <div style={{opacity: keep, marginTop: 6, color: C.ink}}>
          14 sensör + cycle_norm = <span style={{color: C.green, fontWeight: 800}}>15 özellik</span>
        </div>
      </div>

      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <text x={CX0 - 40} y={290} fontSize={32} fontWeight={700}>Arızaya yaklaştıkça sensörler kayar</text>
        <text x={CX0 - 40} y={330} fontSize={26} fill={C.muted}>100 motorun ortalaması, 0-1 ölçeğinde</text>
        {[0, 0.5, 1].map((v) => (
          <g key={v}>
            <line x1={CX0} x2={CX1} y1={lerp(CY1, CY0, v)} y2={lerp(CY1, CY0, v)} stroke={C.grid} strokeWidth={2} />
            <text x={CX0 - 14} y={lerp(CY1, CY0, v) + 9} fontSize={24} fill={C.faint} textAnchor="end">{v}</text>
          </g>
        ))}
        {[125, 100, 75, 50, 25, 0].map((r) => (
          <text key={r} x={lerp(CX0, CX1, (125 - r) / 125)} y={CY1 + 40} fontSize={24} fill={C.faint} textAnchor="middle">{r}</text>
        ))}
        <text x={(CX0 + CX1) / 2} y={CY1 + 84} fontSize={28} fill={C.muted} textAnchor="middle" fontWeight={600}>
          arızaya kalan çevrim  →  0 = arıza anı
        </text>
        {LINES.map((l, li) => {
          const s = sens[l.k as keyof typeof sens];
          const n = s.norm.length;
          const pts: Pt[] = s.norm.map((v, i) => [lerp(CX0, CX1, i / (n - 1)), lerp(CY1, CY0, v)]);
          const t = prog(frame, 50 + li * 40, 90, easeIO);
          const d = partial(pts, t);
          const e = d[d.length - 1];
          return (
            <g key={l.k}>
              <path d={toPath(d)} fill="none" stroke={l.color} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
              <circle cx={e[0]} cy={e[1]} r={10} fill={l.color} opacity={t > 0 ? 1 : 0} />
            </g>
          );
        })}
      </svg>
      <div style={{position: 'absolute', left: CX0 - 40, top: 356, width: 960, display: 'flex', gap: 20, fontSize: 25, fontWeight: 700}}>
        {LINES.map((l, li) => {
          const s = sens[l.k as keyof typeof sens];
          return (
            <div key={l.k} style={{opacity: prog(frame, 50 + li * 40, 14), flex: 1, borderLeft: `8px solid ${l.color}`, paddingLeft: 12}}>
              <div style={{color: l.color}}>{l.name} {l.arrow}</div>
              <div style={{color: C.muted, fontWeight: 500, fontSize: 24}}>{s.raw_first} → {s.raw_last}</div>
            </div>
          );
        })}
      </div>
    </Shell>
  );
};
