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


if __name__ == "__main__":
    train = load("PM_train.txt")
    fig_map()
    fig_lifetimes(train)
    fig_sensor_trends(train)
    fig_flat_sensors(train)
    print("Görseller:", sorted(p.name for p in IMG.glob("*.png")))
