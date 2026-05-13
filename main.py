import os
from dotenv import load_dotenv
import google.generativeai as genai
import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# NOT: Çalıştırmadan önce .env dosyası oluşturup içine
# GEMINI_API_KEY=xxx şeklinde anahtarınızı eklemeyi unutmayın!

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
# 1. Yapılandırma
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name='gemini-3.1-flash-lite')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tüm dış bağlantılara izin verir
    allow_credentials=True,
    allow_methods=["*"], # GET, POST vb. tüm metodlara izin verir
    allow_headers=["*"], # Tüm başlıklara izin verir
)

STOK_DOSYASI = "data/stoklar.json"
SATIS_DOSYASI = "data/satis_guncel.csv"
KARGO_DOSYASI = "data/kargo_tarihli.csv"

def riski_veritabanina_kaydet(musteri, mesaj, analiz):
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    kayit_metni = f"TARİH: {zaman} | MÜŞTERİ: {musteri}\nMESAJ: {mesaj}\nANALİZ: {analiz}\n" + "-"*30 + "\n"

    with open("riskli_kayitlar.txt", "a", encoding="utf-8") as f:
        f.write(kayit_metni)

@app.get("/")
async def ana_sayfa():
    return {"mesaj": "MERGEN API Aktif!"}


@app.post("/mesaj-analiz")
async def analiz_et(mesaj: str, musteri_adi: str = "Bilinmeyen Müşteri"):
    try:
        with open(STOK_DOSYASI, "r", encoding="utf-8") as f:
            stok_rehberi = f.read()
    except:
        stok_rehberi = "Stok bilgisi şu an yüklenemedi."

    prompt = f"""
    Sen profesyonel bir KOBİ asistanısın[cite: 2]. Güncel Ürün Listemiz ve Stoklarımız:
    {stok_rehberi}

    Müşteri ({musteri_adi}) şunu sordu: '{mesaj}'

    GÖREVLERİN:
    1. Hukuki RISK varsa (tehdit, dava vb.): Sadece 'RISK' yaz ve not ekle.
    2. Stokta olan bir ürün soruluyorsa: Fiyat ve stok bilgisi vererek nazikçe cevapla.
    3. Stokta yoksa: Alternatif bir ürün öner (Örn: Zeytinyağı yoksa Ayçiçek yağı gibi).
    4. Kargo soruluyorsa: 'KARGO: [Sipariş No]' formatını kullan.
    Cevabın başına 'AUTO:' koy.
    """

    try:
        response = model.generate_content(prompt)
        analiz_sonucu = response.text

        if "RISK" in analiz_sonucu:
            riski_veritabanina_kaydet(musteri_adi,mesaj, analiz_sonucu)
            return {"durum": "RISKLI", "aksiyon": "Satıcıya Yönlendirildi", "cevap": "Hukuki inceleme gerekiyor."}
        else:
            return {"durum": "NORMAL", "aksiyon": "Otomatik Cevap", "cevap": analiz_sonucu.replace("AUTO:", "").strip()}
    except Exception as e:
        return {"hata": str(e),
                "ipucu": "Eger 404 aliyorsan terminale 'pip install --upgrade google-generativeai' yazmalisin."}


import csv

@app.get("/kargo-sorgula/{satis_id}")
async def kargo_sorgula(satis_id: str):
    try:
        with open(KARGO_DOSYASI, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["satis_id"] == satis_id:
                    return {
                        "siparis_no": row["satis_id"],
                        "alici": row["alici_adi"],
                        "durum": row["kargo_durumu"],
                        "nereden_nereye": f"Depo -> {row['sehir']}",
                        "tarih": row["kargoya_verilis_tarihi"]
                    }
        return {"hata": "Bu sipariş numarasına ait kargo bulunamadı."}
    except FileNotFoundError:
        return {"hata": "Kargo veri dosyası bulunamadı!"}


import json


@app.get("/stok-durumu")
async def stok_listele():
    try:
        with open(STOK_DOSYASI, "r", encoding="utf-8") as f:
            veri = json.load(f)


        for urun in veri:
            stok_miktari = urun.get("stok_miktari", 0)
            stok_esigi = urun.get("stok_esigi", 10)
            urun["durum"] = "KRİTİK" if stok_miktari < stok_esigi else "NORMAL"

        return veri
    except FileNotFoundError:
        return {"hata": "stoklar.json dosyası bulunamadı."}
    except Exception as e:
        return {"hata": f"Bir hata oluştu: {str(e)}"}


@app.get("/satis-tahminleme")
async def satis_tahmini_yap():
    try:
        # 1. Satış geçmişini oku (Sadece son satırları veya özeti almak yeterli)
        with open(SATIS_DOSYASI, mode="r", encoding="utf-8") as f:
            satis_verisi = f.read()[:2000]  # Çok uzunsa ilk 2000 karakteri alalım

        # 2. Stok durumunu oku
        with open(STOK_DOSYASI, "r", encoding="utf-8") as f:
            stok_durumu = f.read()

        # 3. Gemini'ye analiz yaptır
        prompt = f"""
        Sen bir veri analistisin. Aşağıdaki satış geçmişine ve mevcut stoklara bak:

        SATIŞ GEÇMİŞİ (CSV):
        {satis_verisi}

        MEVCUT STOKLAR (JSON):
        {stok_durumu}

        GÖREVİN: 
        1. En çok satan 3 ürün grubunu belirle.
        2. Satış hızına bakarak, gelecek hafta stoku bitebilecek kritik ürünleri tahmin et.
        3. KOBİ sahibine 'Şu üründen stok miktarını artırmalısın' şeklinde tavsiye ver.
        Cevabını profesyonel bir rapor şeklinde hazırla.
        """

        response = model.generate_content(prompt)
        return {"analiz": response.text}

    except Exception as e:
        return {"hata": f"Tahminleme sırasında bir sorun oluştu: {str(e)}"}