# 🎮 Cara Berinteraksi dengan AI

Panduan lengkap untuk berinteraksi dengan Self-Evolving AI Anda.

---

## 🚀 CARA 1: Interactive CLI (Paling Mudah)

**Cocok untuk**: User yang mau kasih feedback manual

```powershell
python interact.py
```

**Cara pakai:**
1. Jalankan perintah di atas
2. AI akan membuat prediksi dari data real
3. Anda nilai: [1] Benar ✓ atau [2] Salah ✗
4. Feedback tersimpan untuk improve AI!

**Output:**
```
🤖 INTERAKSI LANGSUNG DENGAN AI
========================================

Interaksi #1
========================================
[AI] Sedang menganalisis data...

📊 HASIL PREDIKSI:
   Prediction: 1 (Class 1)
   Confidence: 75.3%

❓ Menurut Anda, prediksi ini:
   [1] Benar ✓
   [2] Salah ✗
   [3] Lewati →
   [0] Selesai

Pilih (0-3): 1
[OK] Feedback tersimpan: ✓ Benar
```

---

## 🚀 CARA 2: Auto Interact (Background)

**Cocok untuk**: Generate banyak data dengan cepat

```powershell
# Generate 50 interaksi otomatis
python auto_interact.py -n 50

# Atau 100 interaksi dengan delay 0.5 detik
python auto_interact.py -n 100 -d 0.5

# Background mode (silent)
python auto_interact.py -n 200 -q
```

---

## 🚀 CARA 3: cURL / HTTP Request

**Cocok untuk**: Developer, integrasi dengan aplikasi lain

### 1. Get Sample Data
```bash
curl http://localhost:8000/sample
```

### 2. Make Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "best_model_logistic_regression",
    "session_id": "my_session"
  }'
```

**Response:**
```json
{
  "prediction": 0,
  "confidence": 0.753,
  "model_used": "best_model_logistic_regression",
  "interaction_id": 42
}
```

### 3. Give Feedback
```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "interaction_id": 42,
    "feedback": 1,
    "reason": "Correct prediction"
  }'
```

---

## 🚀 CARA 4: Web Browser (Swagger UI)

**Cocok untuk**: Explore API, test manual

1. Buka browser: http://localhost:8000/docs
2. Klik endpoint yang mau di-test
3. Klik "Try it out"
4. Isi parameter
5. Klik "Execute"

---

## 🚀 CARA 5: Dashboard (Streamlit)

**Cocok untuk**: Visualisasi dan monitoring

```powershell
streamlit run app/dashboard.py
```

Buka http://localhost:8501

### Tab "🔮 Prediction":
- Input features manual
- Lihat prediksi real-time
- Visualisasi confidence

### Tab "🔄 Feedback & Improvement":
- Lihat history interaksi
- Statistik feedback
- Monitor evolusi model

---

## 📊 Cara Kerja Interaksi

```
Anda/Script
    ↓
Kirim data ke AI (predict)
    ↓
AI analisis → Prediksi + Confidence
    ↓
Anda nilai (feedback: ✓ / ✗)
    ↓
Simpan ke database
    ↓
(50+ feedback) → Trigger Retrain
    ↓
Model baru → Lebih akurat!
```

---

## 🎯 Target untuk Evolusi

| Metric | Target | Status |
|--------|--------|--------|
| Interactions | 100+ | Cek dengan `python check_health.py` |
| Feedback | 50+ | Untuk trigger retrain |
| Accuracy | >70% | Model yang bagus |
| Satisfaction | >80% | Feedback positif |

---

## ⚡ Quick Start (1 Menit)

```powershell
# Terminal 1: Start AI
cd C:\AI-Project
python app\real_api_v2.py

# Terminal 2: Interaksi
python interact.py
# Atau auto:
python auto_interact.py -n 50

# Terminal 3: Monitor
streamlit run app\dashboard.py
```

---

## 🎬 Demo Cepat

```powershell
# 1. Generate 100 interaksi otomatis (2 menit)
python auto_interact.py -n 100 -d 1

# 2. Cek hasil
python check_health.py

# 3. Lihat di dashboard
streamlit run app\dashboard.py
```

---

## 💡 Tips

1. **Untuk testing**: Gunakan `auto_interact.py -n 50`
2. **Untuk demo**: Gunakan `interact.py` (interactive)
3. **Untuk integrasi**: Gunakan cURL/HTTP API
4. **Untuk monitoring**: Gunakan Dashboard

**Silakan pilih cara yang paling nyaman!** 🎉
