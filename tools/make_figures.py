"""Ders için görselleri üretir (docs/img/ altına).

Bu dosya eğitim kodunun parçası değil; sadece anlatım görselleri içindir.
Kullanım:  python tools/make_figures.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "docs" / "img"
IMG.mkdir(parents=True, exist_ok=True)

# Renkler (dataviz referans paleti)
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#a8a7a1"
INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": "#d6d5cf", "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True,
    "grid.color": "#ebeae5", "grid.linewidth": 0.8, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 11,
})

COLS = ["id", "cycle", "setting1", "setting2", "setting3"] + [f"s{i}" for i in range(1, 22)]
SENSOR_NAMES = {
    "s1": "T2 fan girişi sıcaklık", "s2": "T24 LPC çıkış sıcaklık",
    "s3": "T30 HPC çıkış sıcaklık", "s4": "T50 LPT çıkış sıcaklık",
    "s5": "P2 fan girişi basınç", "s6": "P15 bypass basınç",
    "s7": "P30 HPC çıkış basınç", "s8": "Nf fan devri",
    "s9": "Nc çekirdek devri", "s10": "EPR basınç oranı",
    "s11": "Ps30 HPC statik basınç", "s12": "phi yakıt/Ps30",
    "s13": "NRf düzeltilmiş fan devri", "s14": "NRc düzeltilmiş çekirdek devri",
    "s15": "BPR bypass oranı", "s16": "farB yakıt-hava oranı",
    "s17": "htBleed bleed entalpisi", "s18": "Nf_dmd istenen fan devri",
    "s19": "PCNfR_dmd istenen düz. fan devri", "s20": "W31 HPT soğutma havası",
    "s21": "W32 LPT soğutma havası",
}


def load(name):
    df = pd.read_csv(ROOT / "data" / name, sep=" ", header=None).iloc[:, :26]
    df.columns = COLS
    return df


def fig_map():
    """Projenin büyük haritası: veri -> model -> sonuç akışı."""
    steps = [
        ("1", "Veriyi tanı", "PM_train / test / truth\n100 motor, 21 sensör"),
        ("2", "Etiketle", "RUL = son çevrim − çevrim\nlabel = RUL ≤ 30 ? 1 : 0"),
        ("3", "Ölçekle", "MinMax: her sütun\n0 ile 1 arasına"),
        ("4", "Pencerele", "50 çevrimlik dilimler\n(örnek, 50, 25)"),
        ("5", "Model kur", "LSTM(100) → LSTM(50)\n→ Dense(1, sigmoid)"),
        ("6", "Eğit", "binary_crossentropy\nadam, early stopping"),
        ("7", "Test et", "Test motorları + truth\nAccuracy, Precision, Recall"),
        ("8", "Raporla", "Grafikler, README,\nsonraki adımlar"),
    ]
    fig, ax = plt.subplots(figsize=(15, 6.2))
    ax.set_xlim(0, 4)
    ax.set_ylim(-0.25, 2.2)
    ax.axis("off")
    phase_color = {0: BLUE, 1: BLUE, 2: BLUE, 3: BLUE, 4: ORANGE, 5: ORANGE, 6: AQUA, 7: AQUA}
    for i, (num, title, body) in enumerate(steps):
        row, col = divmod(i, 4)
        x, y = col + 0.06, 1.15 - row * 1.15
        c = phase_color[i]
        ax.add_patch(FancyBboxPatch((x, y), 0.86, 0.85, boxstyle="round,pad=0.02,rounding_size=0.05",
                                    fc="white", ec=c, lw=2))
        ax.add_patch(FancyBboxPatch((x, y + 0.62), 0.86, 0.23, boxstyle="round,pad=0.02,rounding_size=0.05",
                                    fc=c, ec=c, lw=2))
        ax.text(x + 0.43, y + 0.735, f"Aşama {num} · {title}", ha="center", va="center",
                color="white", fontsize=13, weight="bold")
        ax.text(x + 0.43, y + 0.30, body, ha="center", va="center", color=INK, fontsize=11.5,
                linespacing=1.5)
        if col < 3:
            ax.annotate("", xy=(x + 0.98, y + 0.42), xytext=(x + 0.90, y + 0.42),
                        arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.6))
    ax.annotate("", xy=(0.49, 0.89), xytext=(3.49, 1.12),
                arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.4,
                                connectionstyle="arc3,rad=-0.08", linestyle="--"))
    legend = [(BLUE, "VERİ HAZIRLIĞI  (işin %80'i)"), (ORANGE, "MODEL + EĞİTİM"), (AQUA, "DEĞERLENDİRME")]
    for k, (c, t) in enumerate(legend):
        ax.add_patch(FancyBboxPatch((0.08 + k * 1.3, -0.2), 0.08, 0.08, boxstyle="round,pad=0.01", fc=c, ec=c))
        ax.text(0.2 + k * 1.3, -0.16, t, va="center", fontsize=11, color=INK2)
    ax.set_title("Turbofan motoru arıza tahmini — projenin büyük haritası", fontsize=16,
                 weight="bold", loc="left", pad=12)
    fig.savefig(IMG / "01_harita.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def fig_lifetimes(train):
    life = train.groupby("id")["cycle"].max().sort_values()
    fig, ax = plt.subplots(figsize=(12, 4.2))
    ax.bar(range(len(life)), life.values, color=BLUE, width=0.8)
    ax.axhline(life.mean(), color=INK2, lw=1, ls="--")
    ax.text(1, life.mean() + 6, f"ortalama ≈ {life.mean():.0f} çevrim", color=INK2)
    ax.set_xlabel("Motorlar (ömre göre sıralı) — her çubuk 1 motor")
    ax.set_ylabel("Arızaya kadar çevrim")
    ax.set_title(f"Eğitim verisi: 100 motorun her biri arızalanana kadar çalıştırıldı "
                 f"(en kısa {life.min()}, en uzun {life.max()} çevrim)", loc="left", fontsize=12)
    ax.set_xticks([])
    fig.savefig(IMG / "02_motor_omurleri.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def fig_sensor_trends(train):
    df = train.copy()
    df["rul"] = df.groupby("id")["cycle"].transform("max") - df["cycle"]
    sensors = ["s2", "s3", "s4", "s7", "s11", "s12"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 7.5), sharex=True)
    for ax, s in zip(axes.flat, sensors):
        for _, g in df.groupby("id"):
            ax.plot(-g["rul"], g[s], color=GRAY, lw=0.4, alpha=0.35)
        mean = df[df.rul <= 300].groupby("rul")[s].mean().sort_index()
        ax.plot(-mean.index, mean.values, color=BLUE, lw=2.2)
        ax.axvspan(-30, 0, color=ORANGE, alpha=0.12, lw=0)
        ax.set_title(f"{s} · {SENSOR_NAMES[s]}", loc="left", fontsize=11.5)
        ax.set_xlim(-300, 3)
    for ax in axes[1]:
        ax.set_xlabel("Arızaya kalan çevrim  (0 = arıza anı)")
    fig.suptitle("Motor yıprandıkça sensörler kayıyor — gri: tek tek 100 motor, mavi: ortalama, "
                 "turuncu bölge: son 30 çevrim", x=0.01, ha="left", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(IMG / "03_sensor_trendleri.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def fig_flat_sensors(train):
    """Her sensörün aşınmayla (RUL) ilişkisi; hiç değişmeyenler gri."""
    df = train.copy()
    df["rul"] = df.groupby("id")["cycle"].transform("max") - df["cycle"]
    sensors = [f"s{i}" for i in range(1, 22)]
    flat = df[sensors].std() < 0.002
    corr = df[sensors].corrwith(df["rul"]).abs().fillna(0)
    corr[flat] = 0
    fig, ax = plt.subplots(figsize=(12, 4.4))
    ax.bar(sensors, corr.values, color=BLUE, width=0.75)
    for i, s in enumerate(sensors):
        if flat[s]:
            ax.text(i, 0.01, "sabit", ha="center", va="bottom", fontsize=10, color=INK2, rotation=90)
        else:
            ax.text(i, corr[s] + 0.01, f"{corr[s]:.2f}", ha="center", va="bottom", fontsize=9, color=INK2)
    ax.set_ylim(0, 0.8)
    ax.set_ylabel("|korelasyon| (sensör ↔ kalan ömür)")
    ax.set_title("Hangi sensör aşınmayı haber veriyor? 0'a yakın = habersiz, \"sabit\" = hiç değişmiyor",
                 loc="left", fontsize=12)
    fig.savefig(IMG / "04_sabit_sensorler.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def fig_labeling(train, w1=30):
    """Aşama 2: Motor 1 üzerinde RUL ve etiketin nasıl üretildiği + sınıf dengesi."""
    df = train.copy()
    df["rul"] = df.groupby("id")["cycle"].transform("max") - df["cycle"]
    df["label"] = (df["rul"] <= w1).astype(int)
    e1 = df[df.id == 1]
    cut = e1.loc[e1.label == 1, "cycle"].min()

    fig = plt.figure(figsize=(15, 8.5))
    gs = fig.add_gridspec(3, 3, height_ratios=[1.2, 1.2, 0.6], hspace=0.45, wspace=0.3)
    ax1 = fig.add_subplot(gs[0, :2])
    ax2 = fig.add_subplot(gs[1, :2], sharex=ax1)
    ax3 = fig.add_subplot(gs[2, :2], sharex=ax1)
    ax4 = fig.add_subplot(gs[:, 2])

    ax1.plot(e1.cycle, e1.s4, color=BLUE, lw=1.6)
    ax1.set_title("Motor 1 · s4 (T50 türbin çıkış sıcaklığı) — ham veri", loc="left", fontsize=12)
    ax2.plot(e1.cycle, e1.rul, color=INK2, lw=2)
    ax2.axhline(w1, color=ORANGE, lw=1.2, ls="--")
    ax2.text(3, w1 + 6, "RUL = 30 eşiği", color=ORANGE, fontsize=10)
    ax2.annotate("150. çevrim → RUL = 42", xy=(150, 42), xytext=(100, 150), fontsize=10, color=INK,
                 arrowprops=dict(arrowstyle="-|>", color=INK2))
    ax2.set_title("Ürettiğimiz sütun: RUL = 192 − cycle  (kalan ömür)", loc="left", fontsize=12)
    ax3.fill_between(e1.cycle, e1.label, step="mid", color=ORANGE, alpha=0.9, lw=0)
    ax3.set_yticks([0, 1])
    ax3.set_ylim(-0.1, 1.3)
    ax3.set_title(f"Ürettiğimiz etiket: label = 1 eğer RUL ≤ 30  (çevrim {cut}–192)", loc="left", fontsize=12)
    ax3.set_xlabel("Çevrim (uçuş)")
    for ax in (ax1, ax2):
        ax.axvspan(cut - 0.5, 192.5, color=ORANGE, alpha=0.12, lw=0)
        plt.setp(ax.get_xticklabels(), visible=False)

    counts = df["label"].value_counts().sort_index()
    bars = ax4.bar(["0  (güvenli)", "1  (tehlike)"], counts.values, color=[BLUE, ORANGE], width=0.6)
    for b, v in zip(bars, counts.values):
        ax4.text(b.get_x() + b.get_width() / 2, v + 250, f"{v:,}".replace(",", ".") + f"\n%{v / counts.sum() * 100:.0f}",
                 ha="center", fontsize=11)
    ax4.set_ylim(0, counts.max() * 1.15)
    ax4.grid(axis="x", visible=False)
    ax4.set_title("Tüm eğitim verisi:\nsınıf dengesi", loc="left", fontsize=12)
    ax4.set_ylabel("Satır sayısı")
    fig.suptitle("Aşama 2 · Etiketleme: ham sensör verisine \"doğru cevap\" sütunu yapıştırıyoruz",
                 x=0.01, ha="left", fontsize=14, weight="bold")
    fig.savefig(IMG / "05_etiketleme.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def fig_scaling(train):
    """Aşama 3: ham değerler vs MinMax vs standardizasyon (Motor 1, üç sensör)."""
    sensors = [("s9", "s9 çekirdek devri", BLUE), ("s4", "s4 T50 sıcaklık", ORANGE), ("s11", "s11 Ps30 basınç", AQUA)]
    e1 = train[train.id == 1]
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    titles = ["1) Ham değerler: s9 her şeyi eziyor",
              "2) MinMax: (x − min) / (max − min) → 0…1",
              "3) Standardizasyon: (x − ort) / std → ~ −3…+3"]
    for ax, title, mode in zip(axes, titles, ["raw", "minmax", "z"]):
        for s, name, c in sensors:
            col = train[s]
            if mode == "raw":
                y = e1[s]
            elif mode == "minmax":
                y = (e1[s] - col.min()) / (col.max() - col.min())
            else:
                y = (e1[s] - col.mean()) / col.std()
            ax.plot(e1.cycle, y, color=c, lw=1.4, label=name)
        ax.set_title(title, loc="left", fontsize=12)
        ax.set_xlabel("Motor 1 · çevrim")
    axes[0].set_ylim(0, 10000)
    axes[0].text(5, 8300, "s9 ≈ 9000", color=INK, fontsize=10)
    axes[0].text(5, 1700, "s4 ≈ 1400", color=INK, fontsize=10)
    axes[0].text(5, 400, "s11 ≈ 47 (dibe yapışık)", color=INK, fontsize=10)
    axes[1].axhline(0, color=INK2, lw=0.8); axes[1].axhline(1, color=INK2, lw=0.8)
    axes[0].legend(loc="center right", frameon=False, fontsize=10)
    fig.suptitle("Aşama 3 · Ölçekleme: farklı birimdeki sensörleri aynı cetvele koymak",
                 x=0.01, ha="left", fontsize=14, weight="bold")
    fig.tight_layout()
    fig.savefig(IMG / "06_olcekleme.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def fig_windowing(train, seq_len=50):
    """Aşama 4: kayan pencere fikri ve tek bir pencerenin 'resmi'."""
    from matplotlib.patches import Rectangle

    sensors = [f"s{i}" for i in range(1, 22)]
    feats = ["cycle"] + [c for c in sensors if train[c].std() >= 0.002]
    df = train.copy()
    df["label"] = ((df.groupby("id")["cycle"].transform("max") - df["cycle"]) <= 30).astype(int)
    scaled = (df[feats] - df[feats].min()) / (df[feats].max() - df[feats].min())
    e1 = scaled[df.id == 1].reset_index(drop=True)
    lab = df.loc[df.id == 1, "label"].to_numpy()

    fig = plt.figure(figsize=(16, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.15], width_ratios=[1.5, 1], hspace=0.4, wspace=0.15)
    ax = fig.add_subplot(gs[0, :])
    cyc = np.arange(1, len(e1) + 1)
    ax.plot(cyc, e1["s4"], color=GRAY, lw=1.2)
    windows = [(1, BLUE, "Pencere 1: çevrim 1–50"), (2, AQUA, "Pencere 2: çevrim 2–51"),
               (len(e1) - seq_len + 1, ORANGE, "Pencere 143: çevrim 143–192")]
    for k, (start, c, name) in enumerate(windows):
        end = start + seq_len - 1
        y0 = -0.08 - k * 0.09
        ax.add_patch(Rectangle((start - 0.5, y0), seq_len, 0.05, color=c, alpha=0.85, lw=0))
        ax.plot(end, e1["s4"][end - 1], "o", color=c, ms=9, mec=SURF, mew=2)
        ax.text(start + seq_len + 2 if k < 2 else start - 2, y0 + 0.025,
                f"{name}  →  cevap: label[{end}] = {lab[end - 1]}", va="center", fontsize=10.5,
                ha="left" if k < 2 else "right", color=INK)
    ax.set_ylim(-0.36, 1.0)
    ax.set_xlim(0, 196)
    ax.set_xlabel("Motor 1 · çevrim")
    ax.set_ylabel("s4 (ölçekli)")
    ax.set_title("Pencere birer çevrim kayarak ilerliyor; her pencerenin cevabı SON çevriminin etiketi "
                 "(192 − 50 + 1 = 143 pencere)", loc="left", fontsize=12)

    ax2 = fig.add_subplot(gs[1, 0])
    win = e1.iloc[-seq_len:].to_numpy().T
    im = ax2.imshow(win, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    ax2.set_yticks(range(len(feats)))
    ax2.set_yticklabels(["cycle_norm" if f == "cycle" else f for f in feats], fontsize=9)
    ax2.set_xticks([0, 24, 49])
    ax2.set_xticklabels(["143", "167", "192"])
    ax2.set_xlabel("çevrim")
    ax2.grid(False)
    ax2.set_title("Pencere 143'ün 'resmi': 15 özellik × 50 çevrim\n(koyu = 1'e yakın)", loc="left", fontsize=12)
    fig.colorbar(im, ax=ax2, fraction=0.03, pad=0.01)

    ax3 = fig.add_subplot(gs[1, 1])
    ax3.axis("off")
    ax3.set_title("Modele giden veri bloğu: bir küp", loc="left", fontsize=12)
    for i in range(6):
        ax3.add_patch(FancyBboxPatch((0.12 + i * 0.05, 0.22 + i * 0.06), 0.42, 0.42,
                                     boxstyle="round,pad=0.0,rounding_size=0.02",
                                     fc="white", ec=BLUE, lw=1.5))
    ax3.text(0.33 + 5 * 0.05, 0.43 + 5 * 0.06, "1 pencere\n50 × 15", ha="center", va="center", fontsize=11)
    ax3.text(0.5, 0.06, "X_train.shape = (15731, 50, 15)\n(pencere sayısı, çevrim, özellik)",
             ha="center", fontsize=12, weight="bold", color=INK)
    ax3.text(0.5, -0.04, "100 motor × (ömür − 49) = 20.631 − 100·49 = 15.731 kart", ha="center", fontsize=10.5, color=INK2,
             va="top")
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    fig.suptitle("Aşama 4 · Pencereleme: tek fotoğraf yerine 50 karelik film", x=0.01, ha="left",
                 fontsize=14, weight="bold")
    fig.savefig(IMG / "07_pencereleme.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def fig_model():
    """Aşama 5: LSTM modelinin katmanları ve veri şekilleri."""
    layers = [
        ("Girdi", "50 çevrim ×\n15 özellik", "(50, 15)", GRAY, "0"),
        ("LSTM 100", "her çevrimi okur,\nhafızasını günceller,\nçevrim başına\n100 sayılık özet", "(50, 100)", ORANGE, "46.400"),
        ("Dropout 0.2", "eğitimde nöronların\n%20'si rastgele\nkapalı (ezber önler)", "(50, 100)", GRAY, "0"),
        ("LSTM 50", "50 çevrimin tamamını\n50 sayılık tek bir\nözete sıkıştırır", "(50,)", ORANGE, "30.200"),
        ("Dropout 0.2", "", "(50,)", GRAY, "0"),
        ("Dense 1 · sigmoid", "50 sayıyı tek sayıya\nindirir: 0…1 =\narıza olasılığı", "(1,)", AQUA, "51"),
    ]
    fig, ax = plt.subplots(figsize=(15, 5.6))
    ax.axis("off")
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 1.15)
    for i, (name, desc, shape, c, params) in enumerate(layers):
        x = i + 0.08
        h = 0.62 if "LSTM" in name else (0.42 if "Dense" in name else 0.5)
        y = 0.55 - h / 2
        ax.add_patch(FancyBboxPatch((x, y), 0.84, h, boxstyle="round,pad=0.01,rounding_size=0.04",
                                    fc=c, ec=c, alpha=0.95 if c != GRAY else 0.45))
        ax.text(x + 0.42, 0.55, name, ha="center", va="center", fontsize=13, weight="bold",
                color="white" if c != GRAY else INK)
        ax.text(x + 0.42, y - 0.06, f"çıktı {shape}", ha="center", va="top", fontsize=10.5, color=INK)
        ax.text(x + 0.42, y - 0.13, f"{params} parametre", ha="center", va="top", fontsize=9.5, color=INK2)
        if desc:
            ax.text(x + 0.42, y + h + 0.04, desc, ha="center", va="bottom", fontsize=9.5, color=INK2,
                    linespacing=1.4)
        if i < len(layers) - 1:
            ax.annotate("", xy=(i + 1.08, 0.55), xytext=(i + 0.93, 0.55),
                        arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.5))
    ax.text(0.08, 0.02, "Toplam 76.651 öğrenilebilir parametre (ağırlık). Eğitim = bu sayıları hatayı azaltacak şekilde "
            "ayarlamak.", fontsize=11, color=INK)
    ax.set_title("Aşama 5 · Model: iki katlı LSTM + tek nöronlu karar katmanı", loc="left", fontsize=14,
                 weight="bold")
    fig.savefig(IMG / "08_model.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    train = load("PM_train.txt")
    fig_map()
    fig_lifetimes(train)
    fig_sensor_trends(train)
    fig_flat_sensors(train)
    fig_labeling(train)
    fig_scaling(train)
    fig_windowing(train)
    fig_model()
    print("Görseller:", sorted(p.name for p in IMG.glob("*.png")))
