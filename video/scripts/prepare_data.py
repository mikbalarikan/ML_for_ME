"""Ham veriden (data/, outputs/) video için JSON üretir -> video/src/data/data.json
Çalıştır:  python3 scripts/prepare_data.py   (repo kökünden ya da video/ içinden)
"""
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "src" / "data"
PUB = Path(__file__).resolve().parents[1] / "public"
OUT.mkdir(parents=True, exist_ok=True)
PUB.mkdir(parents=True, exist_ok=True)

COLS = ["id", "cycle", "setting1", "setting2", "setting3"] + [f"s{i}" for i in range(1, 22)]
df = pd.read_csv(ROOT / "data" / "PM_train.txt", sep=r"\s+", header=None).iloc[:, :26]
df.columns = COLS
df = df.sort_values(["id", "cycle"]).reset_index(drop=True)
df["RUL"] = df.groupby("id")["cycle"].transform("max") - df["cycle"]
df["label"] = (df["RUL"] <= 30).astype(int)


def r(x, n=4):
    return [round(float(v), n) for v in x]


# --- 1. Veri: ort. bozulma eğrileri (arızaya kalan çevrim, 125 -> 0), 0-1'e normalize
MAXRUL = 125
sens = {}
for s in ["s4", "s11", "s7"]:
    m = df[df.RUL <= MAXRUL].groupby("RUL")[s].mean().sort_index(ascending=False)  # 125..0
    lo, hi = m.min(), m.max()
    sens[s] = {"raw_first": round(float(m.iloc[0]), 2), "raw_last": round(float(m.iloc[-1]), 2),
               "norm": r((m - lo) / (hi - lo))}
data = {
    "stats": {"engines": int(df.id.nunique()), "rows": int(len(df)), "sensors": 21},
    "degradation": {"maxRul": MAXRUL, "sensors": sens},
}

# --- 2. Etiketleme: motor 1
e1 = df[df.id == 1]
n1 = int(e1.cycle.max())
data["engine1"] = {
    "cycles": n1,
    "rul": [int(v) for v in e1.RUL],
    "label": [int(v) for v in e1.label],
    "firstLabel1Cycle": int(e1[e1.label == 1].cycle.min()),
}
cnt = df.label.value_counts()
data["classBalance"] = {"safe": int(cnt[0]), "danger": int(cnt[1])}

# --- 3. Ölçekleme: s9, s4, s11 ham aralık + motor 1 yörüngesi
sc = {}
for s in ["s9", "s4", "s11"]:
    lo, hi = float(df[s].min()), float(df[s].max())
    v = e1[s].to_numpy()
    sc[s] = {"min": round(lo, 2), "max": round(hi, 2),
             "raw": r(v, 2), "scaled": r((v - lo) / (hi - lo))}
data["scaling"] = sc

# --- 4. Pencereleme: motor 1, s11 (0-1) çizgisi
feat = ["s2", "s3", "s4", "s7", "s8", "s9", "s11", "s12", "s13", "s14", "s15", "s17", "s20", "s21"]
v = e1["s11"].to_numpy(); lo, hi = df.s11.min(), df.s11.max()
data["windowing"] = {"line": r((v - lo) / (hi - lo)), "seq": 50,
                     "trainShape": [int(len(df) - 100 * 49), 50, 15]}
assert len(df) - 100 * 49 == 15731

# --- 5. Eğitim logu (epoch 1-tabanlı)
log = pd.read_csv(ROOT / "outputs" / "training_log.csv")
data["training"] = {
    "epochs": int(len(log)),
    "loss": r(log.loss), "val_loss": r(log.val_loss),
    "best_epoch": int(log.val_loss.idxmin()) + 1,
}

# --- 6. Test
t = pd.read_csv(ROOT / "outputs" / "test_predictions.csv")
y = t.label_gercek.to_numpy(); p = t.olasilik.to_numpy()


def conf(th):
    pr = (p >= th).astype(int)
    tp = int(((pr == 1) & (y == 1)).sum()); fp = int(((pr == 1) & (y == 0)).sum())
    fn = int(((pr == 0) & (y == 1)).sum()); tn = int(((pr == 0) & (y == 0)).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn)
    f1 = 2 * prec * rec / (prec + rec)
    return {"th": th, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "acc": round((tp + tn) / len(t), 3), "prec": round(prec, 3),
            "rec": round(rec, 3), "f1": round(f1, 3)}


data["test"] = {
    "n": int(len(t)),
    "at05": conf(0.5),
    "sweep": [conf(round(th, 2)) for th in np.arange(0.5, 0.1999, -0.01)],
    "engines": [{"id": int(a), "rul": int(b), "y": int(c), "p": round(float(d), 3)}
                for a, b, c, d in zip(t.id, t.RUL_gercek, t.label_gercek, t.olasilik)],
    "logreg": {"acc": 0.925, "prec": 1.0, "rec": 0.72, "f1": 0.837},
}
a = data["test"]["at05"]
assert (a["tn"], a["fp"], a["fn"], a["tp"]) == (68, 0, 4, 21), a
assert data["test"]["sweep"][-1]["rec"] == 0.92 and data["test"]["sweep"][-1]["fp"] == 0

(OUT / "data.json").write_text(json.dumps(data, ensure_ascii=False))
shutil.copy(ROOT / "docs" / "img" / "09_lstm_hafiza.png", PUB / "09_lstm_hafiza.png")
print("ok", (OUT / "data.json").stat().st_size, "bayt;", data["training"]["best_epoch"], data["engine1"]["firstLabel1Cycle"])
