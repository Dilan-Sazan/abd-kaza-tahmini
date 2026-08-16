# ABD Trafik Kazalarinda Kaza Siddetinin Tahmini

Hava durumu, yol tipi ve saat bilgisine gore trafik kazalarinin siddet
derecesini tahmin eden siniflandirma projesi.

## Kapsam

Veri hacmi nedeniyle analiz Florida, New York ve Minnesota eyaletleriyle
sinirlandirilmistir (1.420.236 kayit). Uc eyalet farkli iklim kosullarini
temsil edecek sekilde secilmistir.

## Veri Kaynaklari

- US Accidents (Kaggle) - Ana veri, 7.7M kaza - depoda YOK (3 GB)
- US Census Bureau - Ilce nufusu
- Census Gazetteer - Ilce yuzolcumu
- CDC / NCHS - Kentsel-kirsal siniflandirma

## Kurulum

1. Ana veriyi Kaggle'dan indirip data/raw/ klasorune koyun
2. pip install -r requirements.txt
3. Notebooklari numara sirasiyla calistirin

## Notebooklar

- 00_referans_olustur.ipynb - Dis veri kaynaklarini ilce bazinda birlestirir
- 01_veri_hazirlama.ipynb - Ana veriyi temizler ve zenginlestirir
- 02_eda.ipynb - Kesifsel veri analizi
- 03_model.ipynb - Modelleme
