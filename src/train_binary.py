"""Turbofan motoru: "Bu motor önümüzdeki 30 çevrim içinde arızalanır mı?"

Bu dosyayı derslerde aşama aşama birlikte yazıyoruz.
Referans proje: https://github.com/umbertogriffo/Predictive-Maintenance-using-LSTM

Çalıştırma (repo kökünden):  python src/train_binary.py
"""
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

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

if __name__ == "__main__":
    print("train:", train_df.shape, "| test:", test_df.shape, "| truth:", truth_df.shape)
    print("Atılan sabit sensörler:", CONSTANT_SENSORS)
    print(f"Özellikler ({len(FEATURES)}):", FEATURES)
    print(train_df[["id", "cycle", "s4", "s9", "s11", "RUL", "label"]].iloc[[0, 161, 191]])
    print("Test aralığı:", test_df[FEATURES].min().min().round(3), "...", test_df[FEATURES].max().max().round(3))
