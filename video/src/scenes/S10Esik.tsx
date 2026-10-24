import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Card, Pop, Shell} from '../components';
import data from '../data/data.json';
import {C} from '../theme';
import {easeIO, lerp, prog} from '../utils';

const X0 = 190, X1 = 1250, Y0 = 330, Y1 = 780;
const SAFE_X0 = 220, SAFE_X1 = 640, DANG_X0 = 760, DANG_X1 = 1220;

export const S10Esik: React.FC = () => {
  const frame = useCurrentFrame();
  const th = lerp(0.5, 0.2, prog(frame, 36, 100, easeIO));
  const row = data.test.sweep.reduce((b, r) => (Math.abs(r.th - th) < Math.abs(b.th - th) ? r : b), data.test.sweep[0]);
  const eng = data.test.engines;
  const safe = eng.filter((e) => e.y === 0).sort((a, b) => a.p - b.p);
  const dang = eng.filter((e) => e.y === 1).sort((a, b) => a.p - b.p);
  const py = (p: number) => lerp(Y1, Y0, p);
  const yT = py(th);
  const note = prog(frame, 140, 24);
  return (
    <Shell stage={7} stageName="Test et" title="Eşik ayarı" sub="Model olasılık verir; “tehlike” demek için eşiği biz seçeriz">
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {[0, 0.25, 0.5, 0.75, 1].map((v) => (
          <g key={v}>
            <line x1={X0} x2={X1} y1={py(v)} y2={py(v)} stroke={C.grid} strokeWidth={2} />
            <text x={X0 - 14} y={py(v) + 9} fontSize={24} fill={C.faint} textAnchor="end">{v}</text>
          </g>
        ))}
        <text x={X0 - 100} y={Y0 - 30} fontSize={26} fill={C.muted} fontWeight={600}>modelin arıza olasılığı</text>
        {/* eşik bölgesi */}
        <rect x={X0} y={Y0} width={X1 - X0} height={yT - Y0} fill={C.orange} opacity={0.1} />
        <line x1={X0} x2={X1} y1={yT} y2={yT} stroke={C.orange} strokeWidth={5} />
        <rect x={X1 - 190} y={yT - 22} width={190} height={44} rx={12} fill={C.orange} />
        <text x={X1 - 95} y={yT + 10} fontSize={28} fontWeight={800} fill="#fff" textAnchor="middle">eşik {th.toFixed(2)}</text>
        <text x={X0 + 14} y={Y0 + 34} fontSize={26} fontWeight={800} fill={C.orange}>ALARM bölgesi</text>
        {/* sağlam motorlar */}
        {safe.map((e, i) => {
          const cols = 24;
          const x = SAFE_X0 + ((i % cols) / (cols - 1)) * (SAFE_X1 - SAFE_X0);
          const y = py(e.p) - Math.floor(i / cols) * 0 - ((i * 37) % 5) * 5;
          const alarm = e.p >= th;
          return <circle key={e.id} cx={x} cy={y - 8} r={7} fill={alarm ? C.red : C.green} opacity={0.8} />;
        })}
        {/* tehlikedeki motorlar */}
        {dang.map((e, i) => {
          const x = DANG_X0 + (i / (dang.length - 1)) * (DANG_X1 - DANG_X0);
          const caught = e.p >= th;
          const jump = !caught ? 0 : 1;
          return (
            <g key={e.id}>
              <circle cx={x} cy={py(e.p)} r={14} fill={caught ? C.blue : C.card} stroke={caught ? C.blue : C.red} strokeWidth={4} />
              {!caught && <path d={`M${x - 6} ${py(e.p) - 6} L${x + 6} ${py(e.p) + 6} M${x + 6} ${py(e.p) - 6} L${x - 6} ${py(e.p) + 6}`} stroke={C.red} strokeWidth={3} />}
              {jump > 0 && e.p < 0.5 && e.p >= th && <circle cx={x} cy={py(e.p)} r={24} fill="none" stroke={C.blue} strokeWidth={3} opacity={0.5} />}
            </g>
          );
        })}
        <text x={(SAFE_X0 + SAFE_X1) / 2} y={Y1 + 44} fontSize={26} fontWeight={700} textAnchor="middle" fill={C.green}>gerçekte sağlam (68)</text>
        <text x={(DANG_X0 + DANG_X1) / 2} y={Y1 + 44} fontSize={26} fontWeight={700} textAnchor="middle" fill={C.blue}>gerçekte tehlikede (25)</text>
        {/* slider */}
        <g>
          <text x={X0} y={Y1 + 112} fontSize={26} fontWeight={700} fill={C.muted}>eşik</text>
          <line x1={X0 + 80} x2={X1} y1={Y1 + 102} y2={Y1 + 102} stroke={C.grid} strokeWidth={10} strokeLinecap="round" />
          <line x1={X0 + 80} x2={lerp(X0 + 80, X1, (0.5 - th) / 0.3)} y1={Y1 + 102} y2={Y1 + 102} stroke={C.orange} strokeWidth={10} strokeLinecap="round" />
          <circle cx={lerp(X0 + 80, X1, (0.5 - th) / 0.3)} cy={Y1 + 102} r={20} fill={C.card} stroke={C.orange} strokeWidth={6} />
          <text x={X0 + 80} y={Y1 + 148} fontSize={22} fill={C.faint} textAnchor="middle">0.5</text>
          <text x={X1} y={Y1 + 148} fontSize={22} fill={C.faint} textAnchor="middle">0.2</text>
        </g>
      </svg>

      {/* canlı sonuçlar */}
      <div style={{position: 'absolute', left: 1360, top: 300, width: 464, display: 'flex', flexDirection: 'column', gap: 18}}>
        <Card style={{padding: '16px 28px'}}>
          <div style={{fontSize: 26, fontWeight: 700, color: C.muted}}>recall (yakalama oranı)</div>
          <div style={{fontSize: 80, fontWeight: 800, color: C.orange, fontVariantNumeric: 'tabular-nums', lineHeight: 1.1}}>{row.rec.toFixed(2)}</div>
          <div style={{fontSize: 24, color: C.muted, fontWeight: 600}}>0.84 → 0.92</div>
        </Card>
        <div style={{display: 'flex', gap: 18}}>
          <Card style={{padding: '14px 22px', flex: 1}}>
            <div style={{fontSize: 24, fontWeight: 700, color: C.muted}}>kaçırılan (FN)</div>
            <div style={{fontSize: 64, fontWeight: 800, color: C.red}}>{row.fn}</div>
          </Card>
          <Card style={{padding: '14px 22px', flex: 1}}>
            <div style={{fontSize: 24, fontWeight: 700, color: C.muted}}>boş alarm (FP)</div>
            <div style={{fontSize: 64, fontWeight: 800, color: C.green}}>{row.fp}</div>
          </Card>
        </div>
        <div style={{fontSize: 26, color: C.muted, fontWeight: 600, lineHeight: 1.3}}>
          precision hâlâ <b style={{color: C.ink}}>{row.prec.toFixed(3)}</b>: hiç boş alarm yok
        </div>
      </div>
      <div style={{position: 'absolute', left: 1360, top: 780, width: 464, opacity: note, transform: `translateY(${(1 - note) * 20}px)`}}>
        <Card style={{padding: '18px 26px', borderColor: C.orange, background: C.orangeTint}}>
          <div style={{fontSize: 28, fontWeight: 800, lineHeight: 1.3}}>
            Uçakta kaçırılan arıza, boş alarmdan pahalı → <span style={{color: C.orange}}>recall öncelikli</span>
          </div>
        </Card>
      </div>
      <div style={{position: 'absolute', left: 96, top: 1010, opacity: note, fontSize: 22, color: C.faint, fontWeight: 500}}>
        Not: gösterim amaçlı test verisi; gerçek eşik doğrulama verisinde seçilir.
      </div>
    </Shell>
  );
};
