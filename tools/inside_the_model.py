"""Modelin içine bakış: "kara kutu" değil, sadece çarpma-toplama.

1) Eğitilmiş LSTM'i numpy ile elle hesaplar ve Keras'ın sonucuyla karşılaştırır.
2) İkinci LSTM katmanının hafızasını (h) sağlam ve arızalı bir motor için çizer.
3) Tek bir eğitim adımını (ileri → loss → geri yayılım → Adam) açık açık yapar.

Kullanım (repo kökünden, model eğitilmiş olmalı):  python tools/inside_the_model.py
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import keras  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import tensorflow as tf  # noqa: E402

from train_binary import MODEL_PATH, X_test, X_train, test_ids, y_test, y_train  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "docs" / "img"
BLUE, ORANGE, INK, INK2, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb"


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def lstm_forward(x_seq, kernel, recurrent, bias):
    """Keras LSTM'in birebir numpy karşılığı. Kapı sırası Keras'ta: i, f, c, o."""
    units = recurrent.shape[0]
    h = np.zeros(units)
    c = np.zeros(units)
    hs = []
    for x_t in x_seq:                                  # 50 çevrimi sırayla oku
        z = x_t @ kernel + h @ recurrent + bias        # 4 kapının ham değerleri tek seferde
        i = sigmoid(z[:units])                         # giriş kapısı: yeni bilgiden ne kadar alayım?
        f = sigmoid(z[units:2 * units])                # unut kapısı: eski hafızanın ne kadarını tutayım?
        g = np.tanh(z[2 * units:3 * units])            # aday bilgi (−1…1)
        o = sigmoid(z[3 * units:])                     # çıkış kapısı: hafızanın ne kadarını göstereyim?
        c = f * c + i * g                              # hücre hafızası (uzun süreli)
        h = o * np.tanh(c)                             # gizli durum (kısa süreli / dışarı verilen)
        hs.append(h)
    return np.array(hs)


def manual_predict(model, window):
    lstm1, _, lstm2, _, dense = model.layers
    h1 = lstm_forward(window, *lstm1.get_weights())    # (50, 100)
    h2 = lstm_forward(h1, *lstm2.get_weights())        # (50, 50); son satır = özet
    w, b = dense.get_weights()
    logit = h2[-1] @ w[:, 0] + b[0]                    # 50 sayının ağırlıklı toplamı
    return sigmoid(logit), logit, h2


def bce(y, p):
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


model = keras.models.load_model(MODEL_PATH)
keras_proba = model.predict(X_test, verbose=0).ravel()

# ---------------- 1) Elle ileri hesap ----------------
idx_fail = int(np.argmax(keras_proba))                               # model en emin "tehlike"
idx_ok = int(np.argmin(np.where(y_test == 0, keras_proba, 1)))       # model en emin "sağlam"
print("=== 1) Elle hesap vs Keras ===")
hidden = {}
for name, idx in [("arızaya yakın", idx_fail), ("sağlam", idx_ok)]:
    p, logit, h2 = manual_predict(model, X_test[idx])
    hidden[name] = (test_ids[idx], h2)
    print(f"motor {test_ids[idx]:3d} ({name:13s}) | numpy: {p:.6f} | keras: {keras_proba[idx]:.6f} | "
          f"logit: {logit:+.2f} | gerçek: {int(y_test[idx])} | BCE kaybı: {bce(y_test[idx], np.clip(p, 1e-7, 1 - 1e-7)):.5f}")

# ---------------- 2) Hafıza görselleştirme ----------------
fig, axes = plt.subplots(1, 2, figsize=(15, 5.2), sharey=True)
for ax, (name, (eid, h2)) in zip(axes, hidden.items()):
    im = ax.imshow(h2.T, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_title(f"Motor {eid} · {name}", loc="left", fontsize=12)
    ax.set_xlabel("pencere içindeki çevrim (1 → 50)")
    ax.set_xticks([0, 24, 49])
    ax.set_xticklabels(["1", "25", "50"])
    ax.grid(False)
axes[0].set_ylabel("2. LSTM katmanının 50 hafıza hücresi")
fig.colorbar(im, ax=axes, fraction=0.02, pad=0.01, label="h değeri (−1 … +1)")
fig.suptitle("LSTM'in hafızası çevrim çevrim nasıl doluyor? Son sütun = Dense katmanına giden 50 sayılık özet",
             x=0.01, ha="left", fontsize=13, weight="bold")
fig.savefig(IMG / "09_lstm_hafiza.png", dpi=130, bbox_inches="tight", facecolor=SURF)
plt.close(fig)

# ---------------- 3) Tek eğitim adımı ----------------
print("\n=== 3) Tek bir eğitim adımı (batch = 200 pencere) ===")
keras.utils.set_random_seed(0)
student = keras.models.clone_model(model)              # aynı mimari, RASTGELE ağırlıklar (eğitilmemiş)
student.build((None,) + X_train.shape[1:])
optimizer = keras.optimizers.Adam(learning_rate=0.001)
loss_fn = keras.losses.BinaryCrossentropy()
batch = np.random.default_rng(0).choice(len(X_train), 200, replace=False)
xb, yb = X_train[batch], y_train[batch].reshape(-1, 1)

for step in range(1, 4):
    with tf.GradientTape() as tape:
        pred = student(xb, training=True)              # ileri yayılım (dropout açık)
        loss = loss_fn(yb, pred)                       # hata
    grads = tape.gradient(loss, student.trainable_variables)   # geri yayılım: 76.651 türev
    optimizer.apply_gradients(zip(grads, student.trainable_variables))   # Adam güncellemesi
    gnorm = float(tf.linalg.global_norm(grads))
    print(f"adım {step}: loss = {float(loss):.4f} | gradyan büyüklüğü = {gnorm:.4f}")
print("Gradyan şekilleri:", [tuple(g.shape) for g in grads])
print("Toplam türev sayısı:", sum(int(np.prod(g.shape)) for g in grads))
print("Tam eğitim: 54 epoch × ~75 adım ≈", 54 * int(np.ceil(len(X_train) * 0.95 / 200)), "adım")
