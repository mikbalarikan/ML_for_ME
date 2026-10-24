"""AŞAMA 7 · Test et: eğitilmiş modeli hiç görmediği 93 test motorunda sınar.

Çalıştırma (repo kökünden, önce train_binary.py çalışmış olmalı):  python src/evaluate_binary.py
"""
import keras
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

from train_binary import (FEATURES, MODEL_PATH, OUTPUTS, SEQ_LEN, X_test, X_train, test_df, test_ids,
                          train_df, y_test)

THRESHOLD = 0.5  # olasılık bunun üstündeyse "tehlike" diyoruz

BLUE, ORANGE, AQUA, GRAY, INK, INK2 = "#2a78d6", "#eb6834", "#1baf7a", "#a8a7a1", "#0b0b0b", "#52514e"


def scores(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred),
    }


##################################
# 1) LSTM tahminleri
##################################
model = keras.models.load_model(MODEL_PATH)
proba = model.predict(X_test, verbose=0).ravel()   # her motor için 0…1 arıza olasılığı
y_pred = (proba > THRESHOLD).astype(int)

lstm_scores = scores(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)               # [[TN, FP], [FN, TP]]

##################################
# 2) Kıyas: klasik ML (lojistik regresyon), pencere yok, sadece TEK satır
##################################
# Aynı 15 özellik, ama modele sadece o anki çevrimi gösteriyoruz (geçmiş yok).
baseline = LogisticRegression(max_iter=1000)
baseline.fit(train_df[FEATURES], train_df["label"])
last_rows = test_df.groupby("id").tail(1).set_index("id").loc[test_ids]
base_pred = baseline.predict(last_rows[FEATURES])
base_scores = scores(y_test, base_pred)

##################################
# 3) Kayıt ve grafikler
##################################
results = pd.DataFrame({
    "id": test_ids,
    "RUL_gercek": last_rows["RUL"].to_numpy(),
    "label_gercek": y_test.astype(int),
    "olasilik": proba.round(4),
    "tahmin": y_pred,
})
results.to_csv(OUTPUTS / "test_predictions.csv", index=False)


def plot_confusion(cm, path):
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    names = [["Doğru sessizlik\n(TN)", "Boş alarm\n(FP)"], ["Kaçırılan arıza\n(FN)", "Doğru alarm\n(TP)"]]
    colors = [[AQUA, ORANGE], ["#e34948", AQUA]]
    for i in range(2):
        for j in range(2):
            ax.add_patch(plt.Rectangle((j, 1 - i), 0.97, 0.97, color=colors[i][j], alpha=0.18 if cm[i, j] == 0 else 0.85))
            ax.text(j + 0.485, 1 - i + 0.58, str(cm[i, j]), ha="center", va="center", fontsize=30, weight="bold",
                    color="white" if cm[i, j] else INK2)
            ax.text(j + 0.485, 1 - i + 0.25, names[i][j], ha="center", va="center", fontsize=10.5,
                    color="white" if cm[i, j] else INK2)
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_xticks([0.485, 1.485])
    ax.set_xticklabels(["Model: sağlam (0)", "Model: tehlike (1)"])
    ax.set_yticks([1.485, 0.485])
    ax.set_yticklabels(["Gerçek: sağlam (0)", "Gerçek: tehlike (1)"])
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Karışıklık matrisi · 93 test motoru", loc="left", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_engines(results, path):
    r = results.sort_values("RUL_gercek")
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.axvspan(0, 30, color=ORANGE, alpha=0.1, lw=0)
    ax.axhline(THRESHOLD, color=INK2, lw=1, ls="--")
    ok = r["tahmin"] == r["label_gercek"]
    ax.scatter(r.loc[ok, "RUL_gercek"], r.loc[ok, "olasilik"], s=55, color=BLUE, edgecolor="white", lw=1.5,
               label="doğru tahmin", zorder=3)
    ax.scatter(r.loc[~ok, "RUL_gercek"], r.loc[~ok, "olasilik"], s=110, marker="X", color="#e34948",
               edgecolor="white", lw=1, label="yanlış tahmin", zorder=4)
    wrong = r[~ok].sort_values("olasilik")
    # en alttaki iki etiket sola yazılır ki sağdaki noktalarla çakışmasın
    offsets = [((-14, -10), "right"), ((-14, 10), "right")] + [((14, 0), "left")] * len(wrong)
    for (_, row), (off, ha) in zip(wrong.iterrows(), offsets):
        ax.annotate(f"motor {int(row['id'])} · RUL={int(row['RUL_gercek'])}", (row["RUL_gercek"], row["olasilik"]),
                    xytext=off, textcoords="offset points", fontsize=9, color=INK, va="center", ha=ha)
    ax.text(15, 1.06, "gerçekten tehlikede\n(RUL ≤ 30)", ha="center", fontsize=10, color=ORANGE)
    ax.text(60, THRESHOLD + 0.03, "eşik 0.5", ha="left", fontsize=10, color=INK2)
    ax.set_ylim(-0.05, 1.18)
    ax.set_xlabel("Gerçek kalan ömür (RUL, çevrim)")
    ax.set_ylabel("Modelin arıza olasılığı")
    ax.set_title("Her nokta bir test motoru: sola gittikçe arızaya yakın, yukarı gittikçe model daha emin",
                 loc="left", fontsize=12)
    ax.legend(frameon=False, loc="upper right")
    ax.grid(color="#ebeae5")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_threshold(proba, y_true, path):
    th = np.linspace(0.05, 0.95, 91)
    prec = [precision_score(y_true, proba > t, zero_division=1) for t in th]
    rec = [recall_score(y_true, proba > t) for t in th]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(th, rec, color=ORANGE, lw=2.2, label="recall (yakalanan tehlike)")
    ax.plot(th, prec, color=BLUE, lw=2.2, label="precision (alarmın isabeti)")
    ax.axvline(THRESHOLD, color=INK2, lw=1, ls="--")
    ax.set_xlabel("Eşik (olasılık bunun üstündeyse \"tehlike\")")
    ax.set_ylim(0.5, 1.03)
    ax.set_title("Eşiği düşürürsen recall artar, precision düşer (ve tersi)", loc="left", fontsize=12)
    ax.legend(frameon=False, loc="lower left")
    ax.grid(color="#ebeae5")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


plot_confusion(cm, OUTPUTS / "confusion_matrix.png")
plot_engines(results, OUTPUTS / "test_engines.png")
plot_threshold(proba, y_test, OUTPUTS / "threshold_sweep.png")

if __name__ == "__main__":
    print(f"Test motoru: {len(y_test)} (tehlikede: {int(y_test.sum())}) | pencere: {SEQ_LEN} | eğitim penceresi: {len(X_train)}")
    print("Karışıklık matrisi [[TN, FP], [FN, TP]]:\n", cm)
    table = pd.DataFrame({"LSTM (50 çevrim)": lstm_scores, "Lojistik regresyon (tek satır)": base_scores,
                          "Referans proje (README)": {"accuracy": 0.97, "precision": 0.92, "recall": 1.0, "f1": 0.96}})
    print(table.round(3))
    print("Yanlış tahminler:\n", results[results["tahmin"] != results["label_gercek"]].to_string(index=False))
