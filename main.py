import os
import csv
import json
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai

# .env dosyasındaki değişkenleri yükler
load_dotenv()

# 1. Yapılandırma
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Modül seçimi
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

app = FastAPI()

# CORS Ayarları: Frontend'in erişimi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

def riski_veritabanina_kaydet(musteri, mesaj, analiz):
    """Hukuki risk içeren görüşmeleri yerel bir dosyaya loglar."""
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    kayit_metni = f"TARİH: {zaman} | MÜŞTERİ: {musteri}\nMESAJ: {mesaj}\nANALİZ: {analiz}\n" + "-"*30 + "\n"
    with open("riskli_kayitlar.txt", "a", encoding="utf-8") as f:
        f.write(kayit_metni)

@app.get("/")
async def ana_sayfa():
    return {"mesaj": "MERGEN AI API Aktif!"}

import json # Dosyanın en üstünde olduğundan emin ol

@app.post("/mesaj-analiz")
async def analiz_et(mesaj: str, musteri_adi: str = "Bilinmeyen Müşteri"):
    try:
        # Yedek Kontrol: Gemini hata yaparsa diye manuel kontrol
        riskli_kelimeler = ["mahkeme", "dava", "avukat", "iade", "dolandırıcı", "şikayet", "tüketici hakları"]
        manuel_risk = any(kelime in mesaj.lower() for kelime in riskli_kelimeler)

        with open("stoklar.json", "r", encoding="utf-8") as f:
            stok_rehberi = f.read()

        prompt = f"""
        SİSTEM: MERGEN AI. 
        GÖREV: Mesajı analiz et ve sadece JSON dön.
        STOKLAR: {stok_rehberi}
        MESAJ: {mesaj}

        JSON FORMATI ŞU OLSUN (SADECE JSON):
        {{
            "durum": "RISKLI" veya "NORMAL",
            "cevap": "cevabın",
            "risk_skoru": "0-100"
        }}
        """

        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Markdown temizleme
        if "```json" in text_response:
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif "```" in text_response:
            text_response = text_response.split("```")[1].strip()

        try:
            data = json.loads(text_response)
        except:
            # Eğer Gemini JSON dönmeyi beceremezse manuel kontrol devreye girsin
            data = {
                "durum": "RISKLI" if manuel_risk else "NORMAL",
                "cevap": "Mesajınız sistem tarafından inceleniyor. Müşteri temsilcimiz size dönecektir." if manuel_risk else "Mesajınız alındı.",
                "risk_skoru": "95" if manuel_risk else "10"
            }

        # Eğer manuel kontrol risk bulduysa ama Gemini bulamadıysa yine de RISKLI yap
        if manuel_risk:
            data["durum"] = "RISKLI"
            if data["risk_skoru"] == "10": data["risk_skoru"] = "90"

        if data["durum"] == "RISKLI":
            riski_veritabanina_kaydet(musteri_adi, mesaj, data["cevap"])
        
        return data

    except Exception as e:
        # En kötü durumda bile hata verme, manuel kontrolü kullan
        return {
            "durum": "RISKLI" if manuel_risk else "NORMAL", 
            "cevap": "Teknik inceleme gerekiyor.", 
            "risk_skoru": "85"
        }

@app.get("/stok-durumu")
async def stok_listele():
    try:
        with open("stoklar.json", "r", encoding="utf-8") as f:
            veri = json.load(f)

        # Frontend'in beklediği 'durum' ve anahtarları kontrol et
        for urun in veri:
            stok_miktari = urun.get("stok_miktari", 0)
            stok_esigi = urun.get("stok_esigi", 10)
            urun["durum"] = "KRİTİK" if stok_miktari < stok_esigi else "NORMAL"
            # Frontend urun_id bekliyor, eğer dosyada 'id' varsa eşitle
            if "id" in urun and "urun_id" not in urun:
                urun["urun_id"] = urun["id"]
        
        return veri
    except Exception as e:
        return [{"urun_id": "HATA", "urun_adi": str(e), "stok_miktari": 0, "durum": "KRİTİK"}]

@app.get("/satis-tahminleme")
async def satis_tahmini_yap():
    try:
        # Verileri oku (Hata almamak için kontrol ekledik)
        satis_verisi = "Satış verisi bulunamadı."
        if os.path.exists("satis_guncel.csv"):
            with open("satis_guncel.csv", mode="r", encoding="utf-8") as f:
                satis_verisi = f.read()[:1500]

        prompt = f"Aşağıdaki satış verilerini analiz et ve KOBİ sahibine gelecek hafta için kısa bir strateji ver: {satis_verisi}"
        response = model.generate_content(prompt)
        return {"analiz": response.text}
    except Exception as e:
        return {"analiz": "Tahminleme şu an yapılamıyor."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
