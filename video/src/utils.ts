import {Easing, interpolate} from 'remotion';

export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeIO = Easing.bezier(0.65, 0, 0.35, 1);

/** 0..1 ilerleme: start'tan itibaren dur kare boyunca. */
export const prog = (f: number, start: number, dur: number, e: (t: number) => number = easeOut) =>
  interpolate(f, [start, start + dur], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: e,
  });

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));

/** Binlik ayraç nokta (Türkçe): 20631 -> 20.631 */
export const fmtInt = (n: number) =>
  Math.round(n)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, '.');

export type Pt = [number, number];

/** Noktaların t (0..1) kadarını döndürür (son parça interpolasyonlu). */
export function partial(pts: Pt[], t: number): Pt[] {
  const n = pts.length;
  const x = clamp01(t) * (n - 1);
  const i = Math.floor(x);
  const fr = x - i;
  const out = pts.slice(0, i + 1);
  if (i < n - 1 && fr > 0) {
    out.push([lerp(pts[i][0], pts[i + 1][0], fr), lerp(pts[i][1], pts[i + 1][1], fr)]);
  }
  return out;
}

export const toPath = (pts: Pt[]) =>
  pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
