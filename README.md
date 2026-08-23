# ABD Trafik Kazalarinda Kaza Siddetinin Tahmini

Hava durumu, yol tipi ve saat bilgisine gore trafik kazalarinin siddet
derecesini (Severity, 1-4) tahmin eden siniflandirma projesi.

## Kapsam

Veri hacmi nedeniyle analiz Florida, New York ve Minnesota eyaletleriyle
sinirlandirilmistir. Uc eyalet farkli iklim kosullarini temsil edecek
sekilde secilmistir.

Uc eyaletten 1.420.236 kayit secilmis; ayni kazanin birden fazla kaynaktan
gelen 141.966 tekrar kaydi temizlendikten sonra **1.278.270 kayit**
kalmistir (47 sutun).

Severity dagilimi: %0,66 (1) - %81,69 (2) - %15,78 (3) - %1,87 (4).
Veri dengesizdir; metrik secimi bu nedenle macro-F1'dir.

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

## Tasarim ilkesi: veri hazirligi yalnizca 01'de

Eksik deger doldurma, tekrar eden kayitlarin temizlenmesi, hatali sensor
olcumlerinin duzeltilmesi ve kategori gruplama islemlerinin tamami
01 numarali notebook'ta yapilir. 02 ve 03 dosyayi okuyup dogrudan kullanir,
hicbir temizlik islemini tekrarlamaz.

01, kaydetmeden once cikti dosyasini alti maddede denetler (eksik deger,
tekrar kayit, ilce eslesmesi, sensor araliklari, turetilmis sutunlar, hedef
degiskeni). 02 ve 03 de bastan bu kosullari dogrular; saglanmazsa sessizce
calismak yerine hata verip durur.

## Veri hazirlamada ele alinan dort sorun

**Zaman damgasi bicimi.** Start_Time sutunu veride uc ayri metin biciminde
saklaniyor (`2016-11-30 15:36:03`, `...:00.000000`, `...:16.000000000`) ve
66.290 zaman ani birden fazla bicimde kayitli. Metin olarak farkli, zaman
olarak ayni. Sutun bu nedenle, herhangi bir karsilastirma yapilmadan once
tarih tipine donusturulur; aksi halde tekrar analizi ayni kazanin farkli
bicimde yazilmis iki kaydini ayri olay sayar ve tekrarlarin bir bolumu
temizlenmeden kalir.

**Tekrar eden kayitlar.** Ayni kaza birden fazla trafik API'sinden geldigi
icin veride birden cok kez yer alabiliyor. Bu kayitlar egitim ve test
kumesine dagildiginda model test asamasinda ezberledigi satirla karsilasir
ve skor gercekte oldugundan yuksek cikar (veri sizintisi). ID disindaki tum
sutunlari ayni olan 141.966 kayit temizlenmistir. Tekrarlarin %96,5'i
Severity 2 sinifinda oldugu icin temizlik ayni zamanda sinif dengesizligini
de bir miktar azaltmistir.

**Ilce eslesmesi.** Census verisi "St. Johns", kaza verisi "Saint Johns"
yaziyor. Anahtar uyusmadigi icin 139 kayit ilce nufus bilgisi olmadan
kaliyordu. Iki taraf ayni islevle normallestirilerek sorun giderilmistir.

**Fiziksel olarak imkansiz olcumler.** 174 F sicaklik, 984 mph ruzgar,
0.00 inHg basinc gibi istasyon hatalari eksik olcum sayilip doldurulmustur.

## Modelleme

Metrik olarak macro-F1 kullanilmistir. Veri dengesiz oldugu icin (kazalarin
%81,7'si Severity 2) accuracy yaniltici olur: herkese "2" diyen bir model bile
yaklasik %82 accuracy alir. macro-F1 her sinifi esit agirlikta sayar.

Uc model denenmistir (egitim 1.022.616 / test 255.654 satir, 35 degisken):

| Model | Tip | Test macro-F1 | Accuracy |
|---|---|---|---|
| DummyClassifier | Referans | 0,2248 | 0,8169 |
| Lojistik Regresyon | Dogrusal | 0,3099 | 0,4861 |
| **Random Forest** | **Agac tabanli** | **0,4331** | **0,7019** |

**Secilen model: Random Forest** — baseline'in yaklasik 1,9 kati. Egitim
macro-F1'i 0,4522, test 0,4331; aradaki fark 0,02'nin altinda oldugu icin skor
egitim verisinin ezberlenmesinden kaynaklanmamaktadir.

Dogrusal modelin (0,3099) agac tabanli modelin belirgin gerisinde kalmasi,
degiskenlerle kaza siddeti arasindaki iliskilerin dogrusal olmadigini
gostermektedir. Bu sonuc EDA bulgulariyla uyumludur: saat gibi degiskenlerde
iliski donguseldir, dogrusal bir egilim olarak ifade edilemez.

Random Forest'in accuracy degeri baseline'in altindadir. Bunun nedeni
`class_weight="balanced"` kullanilmasidir: model cogunluk sinifini korumak
yerine nadir siniflari (Severity 1 ve 4) yakalamaya calisir. Calismanin karar
olcutu accuracy degil macro-F1'dir.
