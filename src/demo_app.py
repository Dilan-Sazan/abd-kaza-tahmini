"""
ABD Kaza Şiddeti Tahmini — Canlı Demo
=====================================
Çalıştırma:  streamlit run src/demo_app.py
Önce 03_model.ipynb'deki kaydetme hücresini çalıştırıp
model/kaza_modeli.joblib dosyasını üretmiş olman gerekir.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

st.set_page_config(page_title="Kaza Şiddeti Tahmini", page_icon="🚦", layout="wide")

# ---------------------------------------------------------------- model
@st.cache_resource
def modeli_yukle():
    for aday in ["model/kaza_modeli.joblib", "../model/kaza_modeli.joblib"]:
        if Path(aday).exists():
            return joblib.load(aday)
    return None

paket = modeli_yukle()
if paket is None:
    st.error(
        "model/kaza_modeli.joblib bulunamadı.\n\n"
        "Önce 03_model.ipynb içindeki kaydetme hücresini çalıştır."
    )
    st.stop()

model      = paket["model"]
enc        = paket["encoder"]
SUTUNLAR   = paket["sutunlar"]
KATEGORIK  = paket["kategorik"]
VARSAYILAN = paket["varsayilan"]
SECENEKLER = paket["secenekler"]

# ---------------------------------------------------------------- başlık
st.title("🚦 Kaza Şiddeti Tahmini")
st.caption(
    "Random Forest · Test macro-F1 = 0,4331 · 1.278.270 kayıt (Florida, New York, Minnesota)"
)
st.divider()

# ---------------------------------------------------------------- girdiler
st.sidebar.header("Kaza Koşulları")
st.sidebar.caption("Aşağıdaki değerleri değiştirip tahmini canlı izleyebilirsin.")

girdi = {}


def sec(sutun, etiket):
    """Kategorik sütun için açılır menü — sütun yoksa sessizce atla."""
    if sutun in SECENEKLER:
        vars_ = SECENEKLER[sutun]
        ilk = vars_.index(str(VARSAYILAN[sutun])) if str(VARSAYILAN[sutun]) in vars_ else 0
        girdi[sutun] = st.sidebar.selectbox(etiket, vars_, index=ilk)


def kaydir(sutun, etiket, mn, mx, adim=1.0):
    """Sayısal sütun için kaydırıcı — sütun yoksa sessizce atla."""
    if sutun in SUTUNLAR:
        girdi[sutun] = st.sidebar.slider(
            etiket, float(mn), float(mx), float(VARSAYILAN[sutun]), float(adim)
        )


sec("yol_tipi", "Yol tipi")
sec("hava_durumu", "Hava durumu")
sec("State", "Eyalet")
sec("mevsim", "Mevsim")

st.sidebar.markdown("---")
kaydir("saat", "Saat", 0, 23, 1)
kaydir("Temperature(F)", "Sıcaklık (°F)", -20, 120, 1)
kaydir("Visibility(mi)", "Görüş mesafesi (mil)", 0, 20, 0.5)
kaydir("Precipitation(in)", "Yağış (inç)", 0, 3, 0.05)
kaydir("Wind_Speed(mph)", "Rüzgâr hızı (mph)", 0, 60, 1)

st.sidebar.markdown("---")
if "kentsel_kirsal" in SUTUNLAR:
    kaydir("kentsel_kirsal", "Kentsel–kırsal kodu", 1, 6, 1)
if "nufus_yogunlugu" in SUTUNLAR:
    girdi["nufus_yogunlugu"] = st.sidebar.number_input(
        "Nüfus yoğunluğu (kişi/km²)",
        min_value=0.0, value=float(VARSAYILAN["nufus_yogunlugu"]), step=50.0,
    )

st.sidebar.caption(
    f"Sorulmayan {len(SUTUNLAR) - len(girdi)} değişken için veri setinin "
    "medyan / mod değerleri kullanılıyor."
)

# ---------------------------------------------------------------- tahmin
satir = dict(VARSAYILAN)      # önce tüm sütunları varsayılanla doldur
satir.update(girdi)           # kullanıcının verdiklerini üzerine yaz

df = pd.DataFrame([satir])[SUTUNLAR]          # sütun sırası modelinkiyle aynı olmalı
df[KATEGORIK] = enc.transform(df[KATEGORIK])  # eğitimdeki kodlamanın aynısı
df = df.astype("float32")

tahmin = int(model.predict(df)[0])
olasilik = model.predict_proba(df)[0]

# ---------------------------------------------------------------- çıktı
ACIKLAMA = {
    1: ("Çok düşük etki", "Trafik akışı neredeyse etkilenmez.", "#2E7D32"),
    2: ("Düşük etki", "Kısa süreli, sınırlı bir yavaşlama beklenir.", "#558B2F"),
    3: ("Yüksek etki", "Trafik akışında belirgin aksama beklenir.", "#E8A33D"),
    4: ("Çok yüksek etki", "Uzun süreli, geniş çaplı aksama beklenir.", "#C62828"),
}
baslik, aciklama, renk = ACIKLAMA[tahmin]

sol, sag = st.columns([1, 1.25], gap="large")

with sol:
    st.markdown("##### Tahmin")
    st.markdown(
        f"""
        <div style="background:{renk};border-radius:12px;padding:26px 30px;color:#fff">
          <div style="font-size:13px;opacity:.85;letter-spacing:1px">SEVERITY</div>
          <div style="font-size:64px;font-weight:700;line-height:1.05">{tahmin}</div>
          <div style="font-size:20px;font-weight:600;margin-top:4px">{baslik}</div>
          <div style="font-size:14px;opacity:.9;margin-top:8px">{aciklama}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.metric("Modelin bu tahmine güveni", f"%{olasilik.max()*100:.1f}")

with sag:
    st.markdown("##### Sınıf olasılıkları")
    ol = pd.DataFrame(
        {"Olasılık": olasilik},
        index=[f"Severity {c}" for c in model.classes_],
    )
    st.bar_chart(ol, height=260)
    st.caption(
        "Model her sınıf için bir olasılık üretir; en yüksek olasılıklı sınıf tahmin olarak sunulur."
    )

st.divider()

# ---------------------------------------------------------------- notlar
n1, n2, n3 = st.columns(3)
with n1:
    st.markdown("**Severity ne ölçüyor?**")
    st.caption(
        "Kazanın **trafik akışına etkisini** ölçer, yaralanma şiddetini değil. "
        "1 en düşük, 4 en yüksek etkidir."
    )
with n2:
    st.markdown("**Model neden bazen '2' diyor?**")
    st.caption(
        "Veri setinin %81,69'u Severity 2. Model bu dağılımı öğrenir; "
        "class_weight='balanced' ile seyrek sınıflara ağırlık verilmiştir."
    )
with n3:
    st.markdown("**Sınırlılık**")
    st.caption(
        "Severity 1 ve 4'te recall yüksek, precision düşüktür. Model bu sınıfları "
        "yakalar ancak yanlış pozitif üretir."
    )

with st.expander("Modele gönderilen tam satırı göster"):
    st.caption("Kullanıcının girdiği değerler + kalan sütunlar için medyan/mod varsayılanları")
    st.dataframe(pd.DataFrame([satir]).T.rename(columns={0: "değer"}).astype(str), height=420)
