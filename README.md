# ML for ME — Makine Mühendisleri için Uygulamalı Makine Öğrenmesi

**Proje:** Turbofan uçak motorunun sensör verisine bakıp *"Bu motor önümüzdeki 30 çevrim içinde arızalanır mı?"* sorusunu cevaplayan bir model.
Bu, makine mühendisliğindeki en yaygın ML kullanımlarından biri: **kestirimci bakım (predictive maintenance)**.

- **Referans proje:** [umbertogriffo/Predictive-Maintenance-using-LSTM](https://github.com/umbertogriffo/Predictive-Maintenance-using-LSTM) (⭐ 700+, MIT lisansı)
- **Veri:** NASA C-MAPSS turbofan bozulma simülasyonu (FD001 alt kümesi), ~5,7 MB metin dosyası
- **Model:** Keras LSTM (zaman serisi okuyabilen sinir ağı)

![Büyük harita](docs/img/01_harita.png)

## İlerleme

| Aşama | Konu | Durum | Ders notu |
|---|---|---|---|
| 1 | Veriyi tanı | ✅ | [docs/ders_01_veriyi_tani.md](docs/ders_01_veriyi_tani.md) |
| 2 | Etiketle (RUL ve label) | ⏳ sırada | |
| 3 | Ölçekle (MinMax) | ⬜ | |
| 4 | Pencerele (50 çevrimlik diziler) | ⬜ | |
| 5 | Modeli kur (LSTM) | ⬜ | |
| 6 | Eğit (canlı takip) | ⬜ | |
| 7 | Test et (precision, recall) | ⬜ | |
| 8 | Raporla ve sonraki adımlar | ⬜ | |

## Klasörler

```
ML_for_ME/
├── data/                  ← ham veri (dokunmuyoruz)
│   ├── PM_train.txt       100 motor, arızaya kadar tüm çevrimler  (20.631 satır)
│   ├── PM_test.txt        100 başka motor, arızadan önce kesilmiş (13.096 satır)
│   └── PM_truth.txt       test motorlarının gerçekte kaç çevrim daha dayandığı (100 satır)
├── src/
│   └── train_binary.py    ← birlikte yazdığımız ana kod (aşama aşama büyüyor)
├── tools/
│   └── make_figures.py    ← ders görsellerini üretir (eğitimin parçası değil)
├── docs/                  ← her aşamanın ders notu + görseller
└── outputs/               ← eğitilmiş model, grafikler, loglar (Aşama 6'dan sonra)
```

## Kurulum ve çalıştırma

```bash
pip install -r requirements.txt
python src/train_binary.py
```

## Kaynak ve lisans

Veri dosyaları referans projeden alındı (MIT, © 2019 Umberto Griffo). Verinin asıl kaynağı NASA Ames Prognostics Center of Excellence'ın C-MAPSS veri setidir
(A. Saxena, K. Goebel, D. Simon, N. Eklund, "Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation", PHM 2008).
