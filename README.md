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



---

| Modül                | Görev                                                                       |
| -------------------- | --------------------------------------------------------------------------- |
| `main.py`            | Giriş noktası. Excel’i okuyup veriyi işler ve API çağrılarını tetikler.     |
| `settings.py`        | API base URL, token bilgileri, platform türleri gibi sabitleri içerir.      |
| `reader.py`          | Excel dosyasını satır satır okuyup her satırı bir `dict`'e çevirir.         |
| `processor.py`       | Satırdaki bilgileri kontrol eder, doğru senaryoyu seçip işleme yönlendirir. |
| `auth.py`            | BeyondTrust API’ye token bazlı giriş yapar.                                 |
| `managed_system.py`  | Managed System API işlemlerini içerir.                                      |
| `managed_account.py` | Account ekleme, bağlama işlemleri burada yapılır.                           |
| `application.py`     | Application object işlemleri yapılır.                                       |
| `validators.py`      | Excel verilerinin geçerliliğini kontrol eder.                               |
| `utils.py`           | Ortak string, tarih, hata fonksiyonları gibi yardımcı fonksiyonlar.         |


---- 

yapılan adımlar : 

authenticate oluyor direk ve cookie'ye atamasını yapıyor. 

Satır satır excel'i başarılı şekilde okuyor ç 
