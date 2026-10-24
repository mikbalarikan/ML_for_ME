import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Card, Pop, Shell} from '../components';
import data from '../data/data.json';
import {C, MONO} from '../theme';
import {easeIO, lerp, prog} from '../utils';

const ROWS = [
  {k: 's9', name: 's9 · çekirdek devri', color: C.green},
  {k: 's4', name: 's4 · T50', color: C.orange},
  {k: 's11', name: 's11 · Ps30', color: C.blue},
] as const;
const BX = 330, BW = 780;
const RAW_MAX = 9300;

export const S05Olcek: React.FC = () => {
  const frame = useCurrentFrame();
  const sc = data.scaling;
  const grow = prog(frame, 14, 30);
  const m = prog(frame, 84, 34, easeIO); // ham -> ölçekli
  return (
    <Shell stage={3} stageName="Ölçekle" title="Ölçekle" sub="Sensörler farklı birimlerde; model hepsini aynı cetvelde görmeli">
      <Pop delay={4} style={{position: 'absolute', left: 96, top: 270, fontFamily: MONO, fontSize: 46, fontWeight: 700}}>
        x′ = (x − min) / (max − min)
      </Pop>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {ROWS.map((r, i) => {
          const s = sc[r.k];
          const y = 430 + i * 130;
          const raw = s.raw[0];
          const scaled = s.scaled[0];
          const rawLen = (raw / RAW_MAX) * BW;
          const len = lerp(rawLen, scaled * BW, m) * grow;
          return (
            <g key={r.k}>
              <text x={BX - 24} y={y + 20} fontSize={30} fontWeight={700} textAnchor="end" fill={r.color}>{r.name}</text>
              <rect x={BX} y={y - 8} width={BW} height={44} rx={10} fill={C.grid} opacity={0.55} />
              <rect x={BX} y={y - 8} width={Math.max(len, 5)} height={44} rx={10} fill={r.color} />
              <text x={BX + Math.max(len, 5) + 18} y={y + 24} fontSize={34} fontWeight={800} fill={C.ink}>
                {m < 0.5 ? `≈ ${Math.round(raw)}` : scaled.toFixed(2)}
              </text>
            </g>
          );
        })}
        {/* cetvel */}
        <g opacity={m}>
          {[0, 0.5, 1].map((v) => (
            <g key={v}>
              <line x1={BX + v * BW} x2={BX + v * BW} y1={400} y2={790} stroke={C.faint} strokeWidth={2} strokeDasharray="6 8" />
              <text x={BX + v * BW} y={826} fontSize={26} fill={C.muted} textAnchor="middle" fontWeight={600}>{v}</text>
            </g>
          ))}
        </g>
        <text x={BX} y={826} fontSize={26} fill={C.muted} fontWeight={600} opacity={1 - m}>0</text>
        <text x={BX + BW} y={826} fontSize={26} fill={C.muted} textAnchor="end" fontWeight={600} opacity={1 - m}>9300</text>
      </svg>
      <div style={{position: 'absolute', left: BX, top: 880, fontSize: 32, fontWeight: 700, color: m < 0.5 ? C.red : C.green}}>
        {m < 0.5 ? 'Ham değerler: s9 her şeyi ezer, s11 görünmez' : 'MinMax sonrası: hepsi 0–1 cetvelinde, adil'}
      </div>

      <Pop delay={92} style={{position: 'absolute', left: 1300, top: 380, width: 524}}>
        <Card style={{padding: '24px 30px'}}>
          <div style={{fontSize: 30, fontWeight: 800, marginBottom: 14}}>Altın kural</div>
          <div style={{display: 'flex', alignItems: 'center', gap: 14, marginBottom: 12}}>
            <div style={{background: C.blueTint, color: C.blue, borderRadius: 12, padding: '8px 16px', fontSize: 26, fontWeight: 700}}>Eğitim</div>
            <div style={{fontSize: 26, fontFamily: MONO, color: C.green, fontWeight: 700}}>fit + transform</div>
          </div>
          <div style={{fontSize: 24, color: C.muted, marginBottom: 18}}>min / max yalnızca burada öğrenilir</div>
          <div style={{display: 'flex', alignItems: 'center', gap: 14, marginBottom: 12}}>
            <div style={{background: C.orangeTint, color: C.orange, borderRadius: 12, padding: '8px 16px', fontSize: 26, fontWeight: 700}}>Test</div>
            <div style={{fontSize: 26, fontFamily: MONO, color: C.blue, fontWeight: 700}}>sadece transform</div>
          </div>
          <div style={{fontSize: 24, color: C.muted}}>Testte fit = veri sızıntısı (gelecekten bilgi)</div>
        </Card>
      </Pop>
      <Pop delay={120} style={{position: 'absolute', left: 1300, top: 780, width: 524, fontSize: 36, fontWeight: 800}}>
        <span style={{color: C.red}}>fit</span> sadece <span style={{color: C.blue}}>eğitim</span> verisine!
      </Pop>
    </Shell>
  );
};
