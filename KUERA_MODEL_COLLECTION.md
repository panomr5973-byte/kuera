# KUWERA AI Model Collection

## Daftar Model AI (< 2GB) untuk Integrasi dengan Kuera

---

## Ringkasan

Telah dikumpulkan **8 model AI** dari berbagai sumber (Alibaba, Google, Microsoft, Stability AI, Mistral) dengan total ukuran **7.2 GB** jika semua didownload.

---

## Model yang Direkomendasikan (Top 5)

### 1. Qwen2.5-1.5B-Instruct [⭐ TOP RECOMMENDED]
- **Ukuran**: 0.4 GB
- **Repository**: Qwen/Qwen2.5-1.5B-Instruct-GGUF
- **File**: qwen2.5-1.5b-instruct-q4_k_m.gguf
- **Deskripsi**: Model multilingual Alibaba (1.5B) - ringan & cepat, support Bahasa Indonesia
- **Tags**: indonesian, multilingual, lightweight, recommended
- **Cocok untuk**: Chatbot Bahasa Indonesia, sistem dengan resource terbatas

### 2. Qwen2.5-3B-Instruct [⭐ RECOMMENDED]
- **Ukuran**: 0.8 GB
- **Repository**: Qwen/Qwen2.5-3B-Instruct-GGUF
- **File**: qwen2.5-3b-instruct-q4_k_m.gguf
- **Deskripsi**: Model multilingual Alibaba (3B) - support Bahasa Indonesia
- **Tags**: indonesian, multilingual, balanced, recommended
- **Cocok untuk**: Chatbot Bahasa Indonesia dengan kualitas lebih baik

### 3. Gemma-2-2B-it [⭐ RECOMMENDED]
- **Ukuran**: 0.6 GB
- **Repository**: bartowski/gemma-2-2b-it-GGUF
- **File**: gemma-2-2b-it-Q4_K_M.gguf
- **Deskripsi**: Google Gemma 2 (2B) - model ringan & powerful
- **Tags**: multilingual, google, recommended
- **Cocok untuk**: General purpose chat, tasks kompleks

### 4. Phi-3.5-mini-instruct
- **Ukuran**: 0.9 GB
- **Repository**: microsoft/Phi-3.5-mini-instruct-GGUF
- **File**: Phi-3.5-mini-instruct-Q4_K_M.gguf
- **Deskripsi**: Microsoft Phi-3.5 Mini - latest version, very capable
- **Tags**: multilingual, microsoft, latest
- **Cocok untuk**: General purpose, reasoning tasks

### 5. TinyLlama-1.1B-Chat
- **Ukuran**: 0.3 GB
- **Repository**: TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF
- **File**: tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
- **Deskripsi**: TinyLlama 1.1B - ultra lightweight chat model
- **Tags**: english, ultra-lightweight
- **Cocok untuk**: Resource sangat terbatas, prototyping cepat

---

## Model Tambahan

### 6. StableLM-2-1.6B-Chat
- **Ukuran**: 0.5 GB
- **Repository**: TheBloke/stablelm-2-1_6b-chat-GGUF
- **Deskripsi**: Stability AI StableLM 2 (1.6B) - balanced performance
- **Tags**: balanced

### 7. Qwen2.5-7B-Instruct [HIGH QUALITY]
- **Ukuran**: 1.8 GB
- **Repository**: Qwen/Qwen2.5-7B-Instruct-GGUF
- **Deskripsi**: Model multilingual Alibaba (7B) - best quality, support Bahasa Indonesia
- **Tags**: indonesian, multilingual, high-quality
- **Cocok untuk**: Kualitas tertinggi untuk Bahasa Indonesia

### 8. Mistral-7B-Instruct-v0.3 [HIGH QUALITY]
- **Ukuran**: 1.9 GB
- **Repository**: MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF
- **File**: mistral-7b-instruct-v0.3.Q3_K_S.gguf
- **Deskripsi**: Mistral 7B - high quality (Q3 for smaller size)
- **Tags**: multilingual, high-quality
- **Cocok untuk**: Tasks kompleks, reasoning advanced

---

## Cara Download

### Opsi 1: Download Model Recommended (Top 5)
```bash
python download_models.py recommended
```
Total: ~2.8 GB

### Opsi 2: Download Semua Model
```bash
python download_models.py all
```
Total: ~7.2 GB

### Opsi 3: Cek Status Download
```bash
python download_models.py status
```

### Opsi 4: Download Manual dengan huggingface-cli
```bash
# Install huggingface-cli
pip install huggingface-hub[cli]

# Download model tertentu
huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct-GGUF qwen2.5-1.5b-instruct-q4_k_m.gguf --local-dir models/llm --local-dir-use-symlinks False
```

---

## Struktur Direktori

```
models/
├── llm/
│   ├── llm_registry.json           # Registry model
│   ├── qwen2.5-1.5b-instruct-q4_k_m.gguf
│   ├── qwen2.5-3b-instruct-q4_k_m.gguf
│   ├── gemma-2-2b-it-Q4_K_M.gguf
│   ├── Phi-3.5-mini-instruct-Q4_K_M.gguf
│   ├── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
│   ├── stablelm-2-1_6b-chat.Q4_K_M.gguf
│   ├── qwen2.5-7b-instruct-q4_k_m.gguf
│   └── mistral-7b-instruct-v0.3.Q3_K_S.gguf
└── worldbank/                      # Model ekonomi (sudah ada)
```

---

## Integrasi dengan Kuera

### Langkah 1: Download Model
```bash
python download_models.py recommended
```

### Langkah 2: Install llama-cpp-python
```bash
pip install llama-cpp-python
```

### Langkah 3: Gunakan dalam Chat
```python
from llama_cpp import Llama

# Load model
model = Llama(
    model_path="models/llm/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    n_ctx=2048,
    verbose=False
)

# Chat
output = model(
    "Q: Apa itu AI?\nA:",
    max_tokens=100,
    temperature=0.7
)
print(output['choices'][0]['text'])
```

---

## Rekomendasi Pemilihan Model

| Kebutuhan | Model | Alasan |
|-----------|-------|--------|
| Bahasa Indonesia terbaik | Qwen2.5-3B atau 7B | Alibaba kuat di Asian languages |
| Resource sangat terbatas | TinyLlama-1.1B | Hanya 0.3 GB |
| Balance terbaik | Qwen2.5-1.5B | 0.4 GB, support Indonesia |
| Kualitas tertinggi | Qwen2.5-7B atau Mistral-7B | 7B parameters |
| General purpose | Gemma-2-2B atau Phi-3.5 | Google/Microsoft quality |

---

## Sumber Data

| Model | Developer | URL |
|-------|-----------|-----|
| Qwen2.5 | Alibaba Cloud | https://huggingface.co/Qwen |
| Gemma | Google | https://huggingface.co/google |
| Phi-3.5 | Microsoft | https://huggingface.co/microsoft |
| StableLM | Stability AI | https://huggingface.co/stabilityai |
| Mistral | Mistral AI | https://huggingface.co/mistralai |
| TinyLlama | TinyLlama Team | https://huggingface.co/TinyLlama |

---

## Catatan Penting

1. **Format GGUF**: Semua model dalam format GGUF untuk kompatibilitas dengan llama.cpp
2. **Quantization**: Q4_K_M (4-bit) untuk balance kualitas/ukuran
3. **Hardware**: Semua model bisa berjalan di CPU (tidak perlu GPU)
4. **RAM**: Disarankan minimal 4-8 GB RAM tergantung model
5. **License**: Periksa license masing-masing model sebelum commercial use

---

## File yang Dibuat

- `kuera_model_downloader.py` - Sistem pencarian model
- `create_model_registry.py` - Pembuat registry
- `download_models.py` - Script download
- `models/llm/llm_registry.json` - Database model
- `KUERA_MODEL_COLLECTION.md` - Dokumentasi ini

---

**Status**: Sistem siap untuk download model AI!

Untuk memulai:
```bash
python download_models.py recommended
```
