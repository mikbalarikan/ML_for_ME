"""Turbofan motoru: "Bu motor önümüzdeki 30 çevrim içinde arızalanır mı?"

Bu dosyayı derslerde aşama aşama birlikte yazıyoruz.
Referans proje: https://github.com/umbertogriffo/Predictive-Maintenance-using-LSTM

Çalıştırma (repo kökünden):  python src/train_binary.py
"""
from pathlib import Path

import pandas as pd

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

if __name__ == "__main__":
    print("train:", train_df.shape, "| test:", test_df.shape, "| truth:", truth_df.shape)
    print(train_df[["id", "cycle", "s4", "RUL", "label"]].iloc[[0, 1, 150, 160, 161, 191]])
    print("Etiket dağılımı (train):", train_df["label"].value_counts().to_dict())
