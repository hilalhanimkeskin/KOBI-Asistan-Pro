const API_URL = "http://127.0.0.1:8000";

// Stokları Çekme
async function stoklariGetir() { /* Kodun tamamı */ }

// Mesaj Analizi
async function mesajAnalizEt() { /* Kodun tamamı */ }

// Kargo Sorgulama
async function kargoSorgula() { /* Kodun tamamı */ }

// Satış Tahminleme
async function satisTahminiAl() { /* Kodun tamamı */ }

window.onload = stoklariGetir;

async function aiSoruSor() {
    const soru = document.getElementById('ai-soru').value;
    const isim = document.getElementById('musteri-adi').value || "Müşteri";
    const cevapAlani = document.getElementById('ai-cevap-alani');
    const cevapMetni = document.getElementById('ai-cevap-metni');

    if(!soru) return alert("Soru boş olamaz!");

    cevapAlani.classList.remove('hidden');
    cevapMetni.innerText = "Düşünüyorum...";

    try {
        const res = await fetch(`${API_URL}/mesaj-analiz?mesaj=${encodeURIComponent(soru)}&musteri_adi=${encodeURIComponent(isim)}`, {
            method: 'POST'
        });
        const data = await res.json();
        cevapMetni.innerText = data.cevap;
        
        // Eğer riskliyse çerçeveyi kırmızı yap
        if(data.durum === "RISKLI") {
            cevapAlani.style.borderColor = "#701a35";
        } else {
            cevapAlani.style.borderColor = "#e81cff";
        }
    } catch (e) {
        cevapMetni.innerText = "Hata: Sunucuya bağlanılamadı.";
    }
}
