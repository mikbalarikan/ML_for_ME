import React from 'react';
import {Card, Pop, Shell} from '../components';
import {C, MONO} from '../theme';

const ITEMS = [
  {n: 1, t: 'Veri hazırlığı işin %80’i', s: 'etiketle, ölçekle, pencerele: model sonra gelir', c: C.blue},
  {n: 2, t: 'fit sadece eğitim verisine', s: 'testte fit = veri sızıntısı', c: C.green},
  {n: 3, t: 'Accuracy yanıltabilir', s: 'hep “0” diyen model %85; precision ve recall’a bak', c: C.orange},
  {n: 4, t: 'Eşik bir mühendislik kararı', s: 'kaçırılan arıza > boş alarm → eşiği doğrulama verisinde, recall’a göre seç', c: C.red},
];

export const S11Kapanis: React.FC = () => (
  <Shell stage={8} stageName="Raporla" title="Aklımızda kalanlar" sub="Turbofan motoru arıza tahmini, 8 adımda">
    {ITEMS.map((it, i) => (
      <Pop key={it.n} delay={10 + i * 14} style={{position: 'absolute', left: 96 + (i % 2) * 880, top: 290 + Math.floor(i / 2) * 230, width: 848}}>
        <Card style={{padding: '26px 34px', height: 190, display: 'flex', alignItems: 'center', gap: 28, borderLeft: `10px solid ${it.c}`}}>
          <div style={{fontSize: 76, fontWeight: 800, color: it.c, minWidth: 54}}>{it.n}</div>
          <div>
            <div style={{fontSize: 40, fontWeight: 800, lineHeight: 1.15}}>{it.t}</div>
            <div style={{fontSize: 26, color: C.muted, fontWeight: 500, marginTop: 8, lineHeight: 1.3}}>{it.s}</div>
          </div>
        </Card>
      </Pop>
    ))}
    <Pop delay={80} style={{position: 'absolute', left: 96, top: 790, width: 1728}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 40}}>
        <div style={{fontFamily: MONO, fontSize: 84, fontWeight: 800, color: C.ink, letterSpacing: -2}}>ML_for_ME</div>
        <div style={{fontSize: 30, color: C.muted, fontWeight: 600, lineHeight: 1.35}}>
          Makine mühendisleri için uygulamalı makine öğrenmesi
          <br />
          LSTM · NASA C-MAPSS · Keras
        </div>
      </div>
    </Pop>
    <Pop delay={100} style={{position: 'absolute', left: 100, top: 930, fontSize: 28, color: C.muted, fontWeight: 600}}>
      Sonraki adım: kalan ömrü (RUL) sayı olarak tahmin eden regresyon modeli
    </Pop>
  </Shell>
);
