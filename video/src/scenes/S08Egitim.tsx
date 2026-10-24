import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Card, Pop, Shell} from '../components';
import data from '../data/data.json';
import {C} from '../theme';
import {lerp, partial, prog, toPath, Pt, easeIO} from '../utils';

const X0 = 200, X1 = 1250, Y0 = 400, Y1 = 850;
const YMAX = 0.26;
const NODES = [
  {t: 'Tahmin et', s: 'ileri geçiş', c: C.blue},
  {t: 'Hatayı ölç', s: 'loss', c: C.orange},
  {t: 'Geri yayılım', s: 'suçluyu bul', c: C.red},
  {t: 'Adam', s: 'ağırlıkları düzelt', c: C.green},
];

export const S08Egitim: React.FC = () => {
  const frame = useCurrentFrame();
  const tr = data.training;
  const E = tr.epochs; // 54
  const sx = (e: number) => lerp(X0, X1, (e - 1) / (E - 1 + 1)); // epoch (1-tabanlı)
  const sy = (v: number) => lerp(Y1, Y0, v / YMAX);
  const mk = (arr: number[]): Pt[] => arr.map((v, i) => [sx(i + 1), sy(v)]);
  const lossP = mk(tr.loss), valP = mk(tr.val_loss);
  const t = prog(frame, 20, 190, easeIO);
  const ep = 1 + t * (E - 1); // anlık epoch
  const ei = Math.min(E, Math.floor(ep));
  const dl = partial(lossP, t), dv = partial(valP, t);
  const bestX = sx(tr.best_epoch);
  const stopX = sx(E);
  const showBest = ep >= tr.best_epoch;
  const showStop = ep >= E - 0.01;
  const act = Math.floor(frame / 18) % 4;
  return (
    <Shell stage={6} stageName="Eğit" title="Eğit" sub="1 epoch = 15.731 pencerenin tamamı · batch 200 · en fazla 100 epoch">
      <div style={{position: 'absolute', left: 96, top: 262, fontSize: 32, fontWeight: 700, display: 'flex', gap: 30, whiteSpace: 'nowrap'}}>
        <span>epoch <span style={{color: C.ink, fontVariantNumeric: 'tabular-nums'}}>{ei}</span></span>
        <span style={{color: C.blue}}>loss {tr.loss[ei - 1].toFixed(3)}</span>
        <span style={{color: C.orange}}>val_loss {tr.val_loss[ei - 1].toFixed(3)}</span>
      </div>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {[0, 0.05, 0.1, 0.15, 0.2, 0.25].map((v) => (
          <g key={v}>
            <line x1={X0} x2={X1} y1={sy(v)} y2={sy(v)} stroke={C.grid} strokeWidth={2} />
            <text x={X0 - 14} y={sy(v) + 9} fontSize={24} fill={C.faint} textAnchor="end">{v.toFixed(2)}</text>
          </g>
        ))}
        {[1, 10, 20, 30, 40, 50].map((e) => (
          <text key={e} x={sx(e)} y={Y1 + 40} fontSize={24} fill={C.faint} textAnchor="middle">{e}</text>
        ))}
        <text x={(X0 + X1) / 2} y={Y1 + 84} fontSize={28} fill={C.muted} textAnchor="middle" fontWeight={600}>epoch</text>
        <text x={X0 - 100} y={Y0 - 28} fontSize={26} fill={C.muted} fontWeight={600}>hata (loss)</text>
        <path d={toPath(dl)} fill="none" stroke={C.blue} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
        <path d={toPath(dv)} fill="none" stroke={C.orange} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
        {/* efsane */}
        <g fontSize={26} fontWeight={700}>
          <rect x={X0 + 40} y={Y0 + 2} width={40} height={8} rx={4} fill={C.blue} />
          <text x={X0 + 92} y={Y0 + 14} fill={C.blue}>eğitim (loss)</text>
          <rect x={X0 + 40} y={Y0 + 40} width={40} height={8} rx={4} fill={C.orange} />
          <text x={X0 + 92} y={Y0 + 52} fill={C.orange}>ara sınav (val_loss)</text>
        </g>
        {showBest && (
          <g>
            <line x1={bestX} x2={bestX} y1={Y0 + 214} y2={Y1} stroke={C.green} strokeWidth={3} strokeDasharray="10 8" />
            <circle cx={bestX} cy={sy(tr.val_loss[tr.best_epoch - 1])} r={11} fill={C.card} stroke={C.green} strokeWidth={5} />
            <text x={bestX - 14} y={Y0 + 240} fontSize={28} fontWeight={800} fill={C.green} textAnchor="end">en iyi: epoch 44</text>
            <text x={bestX - 14} y={Y0 + 274} fontSize={24} fontWeight={600} fill={C.muted} textAnchor="end">val_loss 0.036 · model kaydedilir</text>
          </g>
        )}
        {showStop && (
          <g>
            <line x1={stopX} x2={stopX} y1={Y0 + 96} y2={Y1} stroke={C.red} strokeWidth={3} strokeDasharray="10 8" />
            <text x={stopX - 14} y={Y0 + 120} fontSize={28} fontWeight={800} fill={C.red} textAnchor="end">epoch 54: EarlyStopping</text>
            <text x={stopX - 14} y={Y0 + 154} fontSize={24} fontWeight={600} fill={C.muted} textAnchor="end">10 epoch iyileşme yok → dur</text>
          </g>
        )}
      </svg>

      <Pop delay={14} style={{position: 'absolute', left: 1340, top: 262, fontSize: 30, fontWeight: 800}}>Her adımın döngüsü</Pop>
      {NODES.map((n, i) => {
        const col = i % 2, row = Math.floor(i / 2);
        const idx = row === 0 ? col : 3 - col; // saat yönü: 0,1 / 3,2
        const pos = [[0, 0], [1, 0], [1, 1], [0, 1]][i];
        const on = act === i;
        return (
          <Pop key={i} delay={22 + i * 8} style={{position: 'absolute', left: 1340 + pos[0] * 254, top: 330 + pos[1] * 170, width: 230}}>
            <Card
              style={{
                height: 132,
                padding: '14px 18px',
                borderColor: on ? n.c : C.grid,
                background: on ? n.c : C.card,
                color: on ? '#fff' : C.ink,
                transform: `scale(${on ? 1.05 : 1})`,
              }}
            >
              <div style={{fontSize: 26, fontWeight: 800, color: on ? '#fff' : n.c}}>{i + 1}</div>
              <div style={{fontSize: 30, fontWeight: 800, lineHeight: 1.1}}>{n.t}</div>
              <div style={{fontSize: 22, fontWeight: 600, opacity: 0.85, marginTop: 4}}>{n.s}</div>
            </Card>
          </Pop>
        );
      })}
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
        <g fontSize={40} fontWeight={800} fill={C.faint} textAnchor="middle" opacity={prog(frame, 50, 20)}>
          <text x={1582} y={410}>→</text>
          <text x={1710} y={496}>↓</text>
          <text x={1582} y={582}>←</text>
          <text x={1456} y={496}>↑</text>
        </g>
      </svg>
      <Pop delay={60} style={{position: 'absolute', left: 1340, top: 700, width: 484, fontSize: 26, lineHeight: 1.4, color: C.muted, fontWeight: 500}}>
        Epoch 44 sonrası eğitim hatası düşmeye devam ederken ara sınav hatası yükselir: <b style={{color: C.red}}>aşırı öğrenme</b> (ezber).
      </Pop>
    </Shell>
  );
};
