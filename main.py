import google.generativeai as genai
import datetime
from fastapi import FastAPI

# 1. Yapılandırma
genai.configure(api_key="AIzaSyB0WWYBuohH8vexN-cqDgAHjOtbdIO867I")


# Model ismini 'models/' ön eki ile ve en stabil versiyonla tanımlıyoruz
model = genai.GenerativeModel(model_name='gemini-3.1-flash-lite')

app = FastAPI()


def riski_veritabanina_kaydet(musteri, mesaj, analiz):
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Kayıt formatını daha profesyonel hale getirdik
    kayit_metni = f"TARİH: {zaman} | MÜŞTERİ: {musteri}\nMESAJ: {mesaj}\nANALİZ: {analiz}\n" + "-"*30 + "\n"

    with open("riskli_kayitlar.txt", "a", encoding="utf-8") as f:
        f.write(kayit_metni)

@app.get("/")
async def ana_sayfa():
    return {"mesaj": "Smart-Flow API Aktif!"}


@app.post("/mesaj-analiz")
async def analiz_et(mesaj: str, musteri_adi: str = "Bilinmeyen Müşteri"):
    prompt = f"""
    Sen profesyonel bir KOBİ asistanısın[cite: 2]. Müşteri '{musteri_adi}' tarafından gönderilen şu mesajı mesajı analiz et: '{mesaj}'

Görevlerin:
1. Hukuki risk (dava, hakaret, tehdit) varsa: Sadece 'RISK' yaz ve yanına yöneticiye kısa bir not ekle[cite: 26].
2. Normal bir soruysa: Nazikçe cevapla ve başına 'AUTO:' koy[cite: 17, 59].
3. Eğer kullanıcı kargo soruyorsa: 'KARGO: [Sipariş No]' formatında çıktı ver[cite: 18].
"""

    try:
        # generation_config ekleyerek hata riskini azaltıyoruz
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

# Betül gelene kadar kullanacağın örnek kargo verisi [cite: 13, 21]
kargo_veritabanı = {
    "128": {"durum": "Yolda", "tahmini_teslim": "Yarın"},
    "129": {"durum": "Gecikme", "tahmini_teslim": "Bilinmiyor"},
    "130": {"durum": "Teslim Edildi", "tahmini_teslim": "Tamamlandı"}
}

@app.get("/kargo-sorgula/{siparis_no}")
async def kargo_sorgula(siparis_no: str):
    # Bu uctan kargo durumunu cekebilirsin [cite: 24, 25]
    sonuc = kargo_veritabanı.get(siparis_no)
    if sonuc:
        return {"siparis_no": siparis_no, **sonuc}
    return {"hata": "Siparis bulunamadi."}