# 📘 Panduan Swagger UI (http://localhost:8000/docs)

## Cara Menggunakan "Try it out"

### Step 1: Buka Endpoint
Klik pada salah satu endpoint (misalnya `/predict`) untuk membukanya

### Step 2: Klik "Try it out"
Di kanan atas setiap endpoint, ada tombol **"Try it out"**. Klik tombol itu.

### Step 3: Isi Parameter
Setelah klik "Try it out", form akan menjadi editable. Isi parameter yang diperlukan.

### Step 4: Klik "Execute"
Scroll ke bawah, klik tombol **"Execute"** untuk menjalankan request.

---

## Contoh: Membuat Prediksi

### 1. Buka `/predict`
Scroll ke endpoint `POST /predict`, klik untuk membuka

### 2. Klik "Try it out"
Tombol di kanan atas

### 3. Edit Request Body
Ganti dari:
```json
{
  "model_id": "string",
  "input_data": {...},
  "session_id": "string"
}
```

Menjadi:
```json
{
  "model_id": "best_model_logistic_regression",
  "session_id": "test_001"
}
```

**Note:** `input_data` bisa dikosongkan, API akan pakai sample otomatis

### 4. Klik "Execute"

### 5. Lihat Response
Response muncul di bawah, contoh:
```json
{
  "prediction": 0,
  "confidence": 0.753,
  "model_used": "best_model_logistic_regression",
  "interaction_id": 42
}
```

---

## Contoh: Memberi Feedback

### 1. Buka `/feedback`
Endpoint `POST /feedback`

### 2. Klik "Try it out"

### 3. Edit Request Body
```json
{
  "interaction_id": 42,
  "feedback": 1,
  "reason": "Correct prediction"
}
```

- `interaction_id`: ID dari prediksi sebelumnya
- `feedback`: 1 untuk benar, 0 untuk salah
- `reason`: Opsional

### 4. Klik "Execute"

---

## Endpoint yang Tersedia

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/health` | Cek status |
| GET | `/models` | List model |
| GET | `/sample` | Ambil sample data |
| POST | `/predict` | Prediksi |
| POST | `/feedback` | Beri feedback |
| POST | `/predict/batch` | Batch prediction |
| GET | `/compare/{m1}/{m2}` | Bandingkan model |
| GET | `/stats` | Statistik lengkap |

---

## Alternatif: Web Interface Sederhana

Jika Swagger UI sulit, gunakan Web Interface:

```powershell
python web_interface.py
```

Buka: http://localhost:8080

Fitur:
- ✅ Single Prediction (1 klik)
- ✅ Auto Generate (generate banyak sekaligus)
- ✅ Feedback buttons (Correct/Incorrect)
- ✅ Status dashboard

---

## Troubleshooting

### "Cannot connect to API"
- Pastikan API jalan: `python app/real_api_v2.py`
- Cek port 8000 tidak dipakai: `netstat -ano | findstr :8000`

### "Model not found"
- Gunakan model ID yang valid dari `/models`
- Contoh: `best_model_logistic_regression`

### "Collector not available"
- Database mungkin error
- Restart API

---

## Quick Test dengan cURL

```bash
# Get sample
curl http://localhost:8000/sample

# Predict
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"model_id":"best_model_logistic_regression"}'

# Feedback
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"interaction_id":1,"feedback":1}'
```
