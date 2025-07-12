btps_auto_import/
│
├── main.py                       # Uygulamayı başlatan ana dosya
├── config/
│   └── settings.py              # API URL, auth bilgileri, sabitler vs.
│
├── excel/
│   ├── reader.py                # Excel okuma işlemleri burada yapılır
│   └── sample_template.xlsx     # Örnek Excel formatı (giriş için referans)
│
├── api/
│   ├── __init__.py
│   ├── auth.py                  # API authentication token alma
│   ├── managed_system.py        # Managed system ile ilgili API işlemleri
│   ├── managed_account.py       # Account ekleme vs.
│   ├── application.py           # Application ile ilgili işlemler
│   └── utils.py                 # Ortak yardımcı fonksiyonlar
│
├── logic/
│   ├── processor.py             # Excel'den okunan satıra göre işlem senaryoları
│   └── validators.py            # Veri doğrulama işlemleri
│
├── logs/
│   └── import.log               # Log dosyaları buraya
│
├── requirements.txt             # Gerekli Python kütüphaneleri
└── README.md                    # Projenin açıklaması
