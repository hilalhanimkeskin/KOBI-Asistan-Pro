🏹 MERGEN | Akıllı KOBİ Yönetim Ekosistemi
MERGEN, KOBİ'lerin dağınık verilerini (Stok, Satış, Müşteri Mesajları, Lojistik) tek bir merkezde toplayan ve Gemini 3.1 Flash-Lite ile stratejik kararlara dönüştüren yapay zeka destekli bir yönetim panelidir.

🚀 Projenin Vizyonu
KOBİ'lerin en büyük sorunu verisizlik değil, veriyi yorumlayamamaktır. MERGEN; JSON, CSV ve metin tabanlı dağınık verileri asenkron bir mimariyle işleyerek işletme sahiplerine proaktif bir asistanlık hizmeti sunar.

✨ Temel Özellikler
🛡️ LLM Tabanlı Güvenlik ve Risk Filtresi
Sistem, müşteri mesajlarını gerçek zamanlı olarak analiz eder. Gemini 3.1 Flash-Lite motoru sayesinde tehdit, hakaret veya hukuki risk içeren mesajları anında tespit eder, arayüzde "Kritik Risk" uyarısı verir ve bu mesajları tarih damgasıyla riskli_kayitlar.txt dosyasına loglar.

📦 Dinamik Stok ve Eşik Yönetimi
stoklar.json üzerinden tüm ürünlerin envanter takibini yapar. Belirlenen kritik eşik değerinin altına düşen ürünler, dashboard üzerinde bordo renk koduyla vurgulanarak "KRİTİK" durumuyla işaretlenir.

📈 Veri Odaklı Satış Tahminleme
Geçmiş satış verilerini (satis_guncel.csv) analiz ederek, gelecek dönem için satın alma önerileri ve stratejik raporlar hazırlar.

🚚 Akıllı Lojistik Sorgulama
Karmaşık lojistik veri setleri içerisinden sipariş ID'si ile kargo durumunu, alıcı bilgilerini ve güncel teslimat rotasını saniyeler içinde süzüp getirir.

🛠️ Teknik Altyapı
Backend: Python 3.x, FastAPI (Asenkron Mimari)

AI Motoru: Google Gemini 3.1 Flash-Lite

Frontend: HTML5, Tailwind CSS, JavaScript (Fetch API)

Veri Yönetimi: Pydantic (Model Doğrulama), JSON & CSV İşleme

Güvenlik: Python-Dotenv (Environment Variables), CORS Middleware

⚙️ Kurulum ve Çalıştırma
Depoyu Klonlayın:
git clone https://github.com/hilalhanimkeskin/KOBI-Asistan-Pro.git
cd KOBI-Asistan-Pro

Bağımlılıkları Yükleyin:
pip install -r requirements.txt

API Anahtarını Tanımlayın:
Ana dizinde bir .env dosyası oluşturun ve Gemini API anahtarınızı ekleyin:
GOOGLE_API_KEY=your_api_key_here

Sistemi Başlatın:
uvicorn main:app --reload

Arayüze Erişin:
index.html dosyasını tarayıcınızda açarak MERGEN Dashboard'u kullanmaya başlayabilirsiniz.
