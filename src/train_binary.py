"""Turbofan motoru: "Bu motor önümüzdeki 30 çevrim içinde arızalanır mı?"

Bu dosyayı derslerde aşama aşama birlikte yazıyoruz.
Referans proje: https://github.com/umbertogriffo/Predictive-Maintenance-using-LSTM

Çalıştırma (repo kökünden):  python src/train_binary.py
"""
import os
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")  # TensorFlow'un kalabalık loglarını kıs

import matplotlib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

matplotlib.use("Agg")  # ekransız ortamda grafiği dosyaya çiz
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
MODEL_PATH = OUTPUTS / "binary_model.keras"

##################################
# AŞAMA 1 · Veriyi tanı
##################################

# Dosyalarda başlık satırı yok; sütun adlarını biz veriyoruz.
# id: motor numarası, cycle: kaçıncı uçuş çevrimi, setting1-3: çalışma ayarı, s1-s21: sensörler
COLUMNS = ["id", "cycle", "setting1", "setting2", "setting3"] + [f"s{i}" for i in range(1, 22)]


def read_engine_file(name):
    # Sütunlar boşlukla ayrılmış; her satırın sonunda 2 boş sütun var, onları atıyoruz.
    df = pd.read_csv(DATA / name, sep=" ", header=None)
    df = df.iloc[:, :26]
    df.columns = COLUMNS
    return df.sort_values(["id", "cycle"]).reset_index(drop=True)


# train: 100 motor, her biri ARIZALANANA KADAR çalıştırılmış (son satır = arıza anı)
train_df = read_engine_file("PM_train.txt")
# test: 100 başka motor, arızadan ÖNCE bir yerde kayıt kesilmiş
test_df = read_engine_file("PM_test.txt")
# truth: test motorlarının kayıt kesildikten sonra kaç çevrim daha dayandığı (cevap anahtarı)
truth_df = pd.read_csv(DATA / "PM_truth.txt", sep=" ", header=None).iloc[:, :1]
truth_df.columns = ["more"]

##################################
# AŞAMA 2 · Etiketle
##################################

W1 = 30  # uyarı penceresi: "önümüzdeki 30 çevrim içinde arızalanacak mı?"

# TRAIN: her motorun son çevrimi = arıza anı.
# transform("max") her satırın yanına KENDİ motorunun son çevrimini yazar.
train_df["RUL"] = train_df.groupby("id")["cycle"].transform("max") - train_df["cycle"]

# TEST: son kayıt arıza anı değil. Toplam ömür = son kayıtlı çevrim + truth'taki "more".
truth_df["id"] = truth_df.index + 1  # truth'un 1. satırı motor 1'e ait
test_df = test_df.merge(truth_df, on="id")
test_df["RUL"] = test_df.groupby("id")["cycle"].transform("max") + test_df["more"] - test_df["cycle"]
test_df = test_df.drop(columns="more")

# Etiket: RUL <= 30 ise 1 (tehlike), değilse 0 (güvenli)
train_df["label"] = (train_df["RUL"] <= W1).astype(int)
test_df["label"] = (test_df["RUL"] <= W1).astype(int)

##################################
# AŞAMA 3 · Ölçekle
##################################

# Hiç değişmeyen sensörleri (sadece EĞİTİM verisine bakarak) ayıklıyoruz: bilgi taşımıyorlar,
# MinMax'te de payda (max - min) = 0 olur. setting1-2 bu veri setinde tek çalışma koşulunun
# etrafındaki gürültü (RUL ile korelasyonu ~0.003), onları da almıyoruz.
SENSORS = [f"s{i}" for i in range(1, 22)]
CONSTANT_SENSORS = [s for s in SENSORS if train_df[s].std() < 0.002]

# cycle'ın kendisi de bilgi: motor ne kadar yaşlı? Ölçeklenmiş kopyasını özellik yapıyoruz,
# orijinal cycle sütunu sıralama için olduğu gibi kalıyor.
train_df["cycle_norm"] = train_df["cycle"]
test_df["cycle_norm"] = test_df["cycle"]
FEATURES = ["cycle_norm"] + [s for s in SENSORS if s not in CONSTANT_SENSORS]

# fit = min ve max'ı ÖĞREN (sadece eğitim verisinden), transform = formülü UYGULA
scaler = MinMaxScaler()
train_df[FEATURES] = scaler.fit_transform(train_df[FEATURES])
test_df[FEATURES] = scaler.transform(test_df[FEATURES])

##################################
# AŞAMA 4 · Pencerele
##################################

SEQ_LEN = 50  # modele her seferinde son 50 çevrimi gösteriyoruz


def make_windows(df):
    """Her motordan, birer çevrim kayan 50'lik pencereler üretir.

    Pencere = 50 çevrim x 15 özellik'lik tablo. Cevabı = pencerenin SON çevriminin etiketi.
    192 çevrimlik motor -> 192 - 50 + 1 = 143 pencere.
    """
    X, y = [], []
    for _, engine in df.groupby("id"):
        values = engine[FEATURES].to_numpy(dtype="float32")
        labels = engine["label"].to_numpy(dtype="float32")
        for end in range(SEQ_LEN, len(engine) + 1):
            X.append(values[end - SEQ_LEN:end])
            y.append(labels[end - 1])
    return np.array(X), np.array(y)


def last_windows(df):
    """Test için: her motordan sadece SON pencere ("bu motor şu an tehlikede mi?").

    50 çevrimden kısa kaydı olan motorlar pencereye sığmadığı için atlanır.
    """
    X, y, ids = [], [], []
    for engine_id, engine in df.groupby("id"):
        if len(engine) < SEQ_LEN:
            continue
        X.append(engine[FEATURES].to_numpy(dtype="float32")[-SEQ_LEN:])
        y.append(engine["label"].iloc[-1])
        ids.append(engine_id)
    return np.array(X), np.array(y, dtype="float32"), ids


X_train, y_train = make_windows(train_df)
X_test, y_test, test_ids = last_windows(test_df)

##################################
# AŞAMA 5 · Modeli kur
##################################


def build_model(n_features):
    import keras

    model = keras.Sequential([
        keras.Input(shape=(SEQ_LEN, n_features)),         # girdi: 50 çevrim x 15 özellik
        keras.layers.LSTM(100, return_sequences=True),     # 1. hafıza katmanı: her çevrimde 100 sayılık özet
        keras.layers.Dropout(0.2),                         # her adımda nöronların %20'sini rastgele kapat (ezberlemesin)
        keras.layers.LSTM(50),                             # 2. hafıza katmanı: 50 çevrimin tamamını 50 sayıya özetle
        keras.layers.Dropout(0.2),
        keras.layers.Dense(1, activation="sigmoid"),       # çıktı: 0 ile 1 arası "arıza olasılığı"
    ])
    model.compile(
        loss="binary_crossentropy",   # 0/1 sorularında hatayı ölçen cetvel
        optimizer="adam",             # ağırlıkları her adımda hatayı azaltacak yöne iten algoritma
        metrics=["accuracy", keras.metrics.Recall(name="recall")],
    )
    return model


##################################
# AŞAMA 6 · Eğit
##################################


def plot_history(history, path):
    """Eğitim eğrilerini çizer (her epoch sonunda güncellenir)."""
    epochs = range(1, len(history["loss"]) + 1)
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    panels = [("loss", "Hata (loss) — düşmeli"), ("accuracy", "Doğruluk (accuracy)"),
              ("recall", "Recall — tehlikeli motorların yakalanan oranı")]
    for ax, (key, title) in zip(axes, panels):
        ax.plot(epochs, history[key], color="#2a78d6", lw=2, marker="o", ms=3, label="eğitim")
        ax.plot(epochs, history["val_" + key], color="#eb6834", lw=2, marker="o", ms=3, label="doğrulama")
        ax.set_title(title, loc="left")
        ax.set_xlabel("epoch")
        ax.grid(color="#ebeae5")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False)
    fig.suptitle(f"Aşama 6 · Canlı eğitim takibi — epoch {len(epochs)}", x=0.01, ha="left",
                 fontsize=14, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def train():
    import keras

    OUTPUTS.mkdir(exist_ok=True)
    keras.utils.set_random_seed(1234)  # aynı sonucu tekrar alabilmek için

    model = build_model(n_features=X_train.shape[2])
    model.summary()

    history = {}

    class LiveProgress(keras.callbacks.Callback):
        def on_epoch_end(self, epoch, logs=None):
            for k, v in logs.items():
                history.setdefault(k, []).append(float(v))
            plot_history(history, OUTPUTS / "training_progress.png")
            print(f"epoch {epoch + 1:3d} | loss {logs['loss']:.4f} | val_loss {logs['val_loss']:.4f} | "
                  f"acc {logs['accuracy']:.3f} | val_acc {logs['val_accuracy']:.3f} | "
                  f"val_recall {logs['val_recall']:.3f}", flush=True)

    model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=200,          # ağırlıklar her 200 pencerede bir güncellenir
        validation_split=0.05,   # son %5 (= son ~5 motor) eğitime girmez, ara sınav olarak kullanılır
        verbose=0,
        callbacks=[
            # doğrulama hatası 10 epoch boyunca iyileşmezse dur, en iyi ağırlıklara geri dön
            keras.callbacks.EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
            keras.callbacks.ModelCheckpoint(MODEL_PATH, monitor="val_loss", save_best_only=True),
            keras.callbacks.CSVLogger(OUTPUTS / "training_log.csv"),
            LiveProgress(),
        ],
    )
    print("En iyi model kaydedildi:", MODEL_PATH)


if __name__ == "__main__":
    print("Atılan sabit sensörler:", CONSTANT_SENSORS)
    print(f"Özellikler ({len(FEATURES)}):", FEATURES)
    print("X_train:", X_train.shape, "| y_train:", y_train.shape, "| tehlike oranı:", y_train.mean().round(3))
    print("X_test :", X_test.shape, "| y_test :", y_test.shape, "| tehlikedeki test motoru:", int(y_test.sum()))
    train()
