import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Pop, Shell} from '../components';
import data from '../data/data.json';
import {C, MONO} from '../theme';
import {easeIO, fmtInt, lerp, partial, prog, toPath, Pt} from '../utils';

const X0 = 130, X1 = 1790, Y0 = 330, Y1 = 520;
const SEQ = 50;
const CW = 300, CH = 190; // kart ölçüsü
const SX = 1010, SY = 950; // kart yığınının sol-alt köşesi
const SHOWN = 36;

export const S06Pencere: React.FC = () => {
  const frame = useCurrentFrame();
  const line = data.windowing.line;
  const N = line.length; // 192
  const nWin = N - SEQ + 1; // 143
  const pts: Pt[] = line.map((v, i) => [lerp(X0, X1, i / (N - 1)), lerp(Y1, Y0, v)]);
  const drawn = partial(pts, prog(frame, 6, 36));
  const slide = prog(frame, 56, 120, easeIO);
  const k = Math.min(nWin, Math.max(0, Math.floor(slide * nWin + 0.0001))); // oluşan pencere sayısı
  const w0 = Math.min(nWin - 1, Math.floor(slide * (nWin - 1))); // şu anki başlangıç indeksi
  const px = lerp(X0, X1, w0 / (N - 1));
  const pw = (SEQ / (N - 1)) * (X1 - X0);
  const all = prog(frame, 190, 46, easeIO); // x100 motor
  const count = lerp(k, 15731, all);
  const shownCards = all > 0.01 ? SHOWN : Math.min(SHOWN, Math.ceil((k / nWin) * SHOWN));
  const slice = pts.slice(w0, w0 + SEQ);
  const sMinX = slice[0]?.[0] ?? 0;
  // kart içindeki mini çizgi
  const mini = slice.map(([x, y]) => [lerp(SX + 24, SX + CW - 24, (x - sMinX) / pw), lerp(SY - 30, SY - CH + 30, (Y1 - y) / (Y1 - Y0))] as Pt);
  const dx = 3.2 + all * 1.6, dy = 3.0 + all * 1.4;
  return (
    <Shell stage={4} stageName="Pencerele" title="Pencerele" sub="Tek çevrim gürültülü: modele fotoğraf değil, son 50 çevrimlik film göster">
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <text x={X0} y={Y0 - 30} fontSize={28} fill={C.muted} fontWeight={600}>Motor 1 · s11 (Ps30), 0–1 ölçeğinde · 192 çevrim</text>
        <line x1={X0} x2={X1} y1={Y1 + 10} y2={Y1 + 10} stroke={C.grid} strokeWidth={2} />
        <path d={toPath(drawn)} fill="none" stroke={C.blue} strokeWidth={4} strokeLinejoin="round" opacity={0.9} />
        {/* pencere */}
        <g opacity={prog(frame, 50, 10)}>
          <rect x={px} y={Y0 - 14} width={pw} height={Y1 - Y0 + 40} rx={12} fill={C.orange} opacity={0.16} />
          <rect x={px} y={Y0 - 14} width={pw} height={Y1 - Y0 + 40} rx={12} fill="none" stroke={C.orange} strokeWidth={4} />
          <text x={px + pw / 2} y={Y1 + 70} fontSize={28} fontWeight={800} fill={C.orange} textAnchor="middle">50 çevrim</text>
        </g>
        {/* kart yığını */}
        {Array.from({length: shownCards}).map((_, j) => {
          const idx = shownCards - 1 - j; // arkadan öne
          return <rect key={idx} x={SX + idx * dx} y={SY - idx * dy - CH} width={CW} height={CH} rx={10} fill={C.card} stroke={idx === 0 ? C.blue : C.faint} strokeWidth={idx === 0 ? 3 : 1.5} />;
        })}
        {/* ön kart içeriği */}
        <rect x={SX} y={SY - CH} width={CW} height={CH} rx={10} fill={C.card} stroke={C.blue} strokeWidth={3} opacity={k > 0 ? 1 : 0} />
        {k > 0 && <path d={toPath(mini)} fill="none" stroke={C.blue} strokeWidth={3} />}
        <text x={SX + CW / 2} y={SY + 36} fontSize={26} fill={C.muted} textAnchor="middle" fontWeight={600} opacity={all}>50 çevrim</text>
        <text x={SX - 18} y={SY - CH / 2} fontSize={26} fill={C.muted} textAnchor="middle" fontWeight={600} opacity={all} transform={`rotate(-90 ${SX - 18} ${SY - CH / 2})`}>15 özellik</text>
        <text x={SX + CW + SHOWN * dx + 14} y={SY - SHOWN * dy - CH / 2} fontSize={26} fill={C.orange} fontWeight={700} opacity={all}>pencere sayısı</text>
      </svg>

      <div style={{position: 'absolute', left: 96, top: 640, width: 800}}>
        <div style={{fontSize: 34, fontWeight: 600, color: C.muted}}>Pencere kaydıkça bir kart eklenir</div>
        <div style={{fontSize: 40, fontWeight: 800, marginTop: 14}}>
          Motor 1: 192 − 50 + 1 ={' '}
          <span style={{color: C.orange}}>{nWin}</span> pencere
        </div>
        <div style={{marginTop: 12, fontSize: 28, fontWeight: 600, color: C.muted, fontVariantNumeric: 'tabular-nums'}}>
          kart: <span style={{color: C.ink, fontWeight: 800}}>{all > 0.01 ? nWin : k}</span> / {nWin}
        </div>
        <div style={{opacity: all, marginTop: 20, fontSize: 34, fontWeight: 600, color: C.muted}}>
          × 100 motor = <span style={{color: C.ink, fontWeight: 800, fontVariantNumeric: 'tabular-nums'}}>{fmtInt(count)}</span> pencere
        </div>
      </div>
      <Pop delay={206} style={{position: 'absolute', left: 96, top: 880, fontFamily: MONO, fontSize: 64, fontWeight: 800, color: C.blue}}>
        (15731, 50, 15)
      </Pop>
      <Pop delay={216} style={{position: 'absolute', left: 96, top: 970, fontSize: 28, color: C.muted, fontWeight: 600}}>
        pencere · çevrim · özellik
      </Pop>
    </Shell>
  );
};
