# Manual Download Guide - KUWERA AI Models

## Status Download Saat Ini

### ✅ Sudah Ada (Ready to Use)
- **Qwen2.5-1.5B-Instruct** (1.04 GB)
- **TinyLlama-1.1B-Chat** (0.62 GB)
- **Total**: 1.66 GB

### ⏳ Perlu Download (8 Models)
- **Total**: ~8.4 GB
- **Estimasi Waktu**: 2-4 jam (tergantung koneksi)

---

## CARA DOWNLOAD MANUAL

### Opsi 1: Download Satu per Satu (Recommended)

Buka terminal/command prompt dan jalankan perintah berikut satu per satu:

#### 1. Qwen2.5-3B (0.8 GB) - PRIORITAS TINGGI
```bash
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='Qwen/Qwen2.5-3B-Instruct-GGUF', filename='qwen2.5-3b-instruct-q4_k_m.gguf', local_dir='models/llm')"
```

#### 2. SeaLLM-7B (1.9 GB) - Southeast Asia
```bash
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='SeaLLMs/SeaLLM-7B-v2-GGUF', filename='seallm-7b-v2-q4_k_m.gguf', local_dir='models/llm')"
```

#### 3. Merak-7B (1.9 GB) - Buatan Indonesia
```bash
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='Ichsan2895/Merak-7B-v4-GGUF', filename='merak-7b-v4-q4_k_m.gguf', local_dir='models/llm')"
```

#### 4. Llama-3.2-3B (0.8 GB) - Multilingual
```bash
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='bartowski/Llama-3.2-3B-Instruct-GGUF', filename='Llama-3.2-3B-Instruct-Q4_K_M.gguf', local_dir='models/llm')"
```

#### 5. Gemma-2-2B (0.6 GB) - Google
```bash
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='bartowski/gemma-2-2b-it-GGUF', filename='gemma-2-2b-it-Q4_K_M.gguf', local_dir='models/llm')"
```

#### 6. Phi-3.5-mini (0.9 GB) - Microsoft
```bash
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='microsoft/Phi-3.5-mini-instruct-GGUF', filename='Phi-3.5-mini-instruct-Q4_K_M.gguf', local_dir='models/llm')"
```

#### 7. Command-R (1.0 GB) - Long Context
```bash
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='bartowski/c4ai-command-r-v01-GGUF', filename='c4ai-command-r-v01-Q4_K_M.gguf', local_dir='models/llm')"
```

#### 8. StableLM-2-1.6B (0.5 GB) - Balanced
```bash
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='TheBloke/stablelm-2-1_6b-chat-GGUF', filename='stablelm-2-1_6b-chat.Q4_K_M.gguf', local_dir='models/llm')"
```

---

### Opsi 2: Download dengan HuggingFace CLI

#### Install CLI:
```bash
pip install huggingface-hub[cli]
```

#### Download semua:
```bash
# Qwen2.5-3B
huggingface-cli download Qwen/Qwen2.5-3B-Instruct-GGUF qwen2.5-3b-instruct-q4_k_m.gguf --local-dir models/llm

# SeaLLM-7B
huggingface-cli download SeaLLMs/SeaLLM-7B-v2-GGUF seallm-7b-v2-q4_k_m.gguf --local-dir models/llm

# Merak-7B
huggingface-cli download Ichsan2895/Merak-7B-v4-GGUF merak-7b-v4-q4_k_m.gguf --local-dir models/llm

# Llama-3.2-3B
huggingface-cli download bartowski/Llama-3.2-3B-Instruct-GGUF Llama-3.2-3B-Instruct-Q4_K_M.gguf --local-dir models/llm

# Gemma-2-2B
huggingface-cli download bartowski/gemma-2-2b-it-GGUF gemma-2-2b-it-Q4_K_M.gguf --local-dir models/llm

# Phi-3.5-mini
huggingface-cli download microsoft/Phi-3.5-mini-instruct-GGUF Phi-3.5-mini-instruct-Q4_K_M.gguf --local-dir models/llm

# Command-R
huggingface-cli download bartowski/c4ai-command-r-v01-GGUF c4ai-command-r-v01-Q4_K_M.gguf --local-dir models/llm

# StableLM-2-1.6B
huggingface-cli download TheBloke/stablelm-2-1_6b-chat-GGUF stablelm-2-1_6b-chat.Q4_K_M.gguf --local-dir models/llm
```

---

### Opsi 3: Download dengan Browser (Manual)

Jika command line bermasalah, download langsung dari browser:

1. Buka https://huggingface.co
2. Cari model (contoh: "Qwen/Qwen2.5-3B-Instruct-GGUF")
3. Click "Files and versions"
4. Download file `.gguf` (pilih yang Q4_K_M)
5. Save ke folder `models/llm/`

**URL Langsung**:
- Qwen2.5-3B: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF
- SeaLLM-7B: https://huggingface.co/SeaLLMs/SeaLLM-7B-v2-GGUF
- Merak-7B: https://huggingface.co/Ichsan2895/Merak-7B-v4-GGUF
- Llama-3.2-3B: https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF
- Gemma-2-2B: https://huggingface.co/bartowski/gemma-2-2b-it-GGUF
- Phi-3.5-mini: https://huggingface.co/microsoft/Phi-3.5-mini-instruct-GGUF
- Command-R: https://huggingface.co/bartowski/c4ai-command-r-v01-GGUF
- StableLM-2-1.6B: https://huggingface.co/TheBloke/stablelm-2-1_6b-chat-GGUF

---

## REKOMENDASI URUTAN DOWNLOAD

### Phase 1: Bahasa Indonesia (Wajib)
1. **Qwen2.5-3B** (0.8 GB) - Bahasa Indonesia terbaik
2. **SeaLLM-7B** (1.9 GB) - Southeast Asia
3. **Merak-7B** (1.9 GB) - Buatan Indonesia

**Total**: 4.6 GB | **Waktu**: ~1-1.5 jam

### Phase 2: Multilingual & Specialized
4. **Llama-3.2-3B** (0.8 GB) - Multilingual
5. **Gemma-2-2B** (0.6 GB) - Google Quality
6. **Phi-3.5-mini** (0.9 GB) - Microsoft

**Total**: 2.3 GB | **Waktu**: ~30-45 menit

### Phase 3: Specialized
7. **Command-R** (1.0 GB) - Long Context
8. **StableLM-2-1.6B** (0.5 GB) - Balanced

**Total**: 1.5 GB | **Waktu**: ~20-30 menit

---

## SETELAH DOWNLOAD

### Verifikasi:
```bash
python -c "from pathlib import Path; [print(f'{f.name}: {f.stat().st_size/1024**3:.2f} GB') for f in sorted(Path('models/llm').glob('*.gguf'))]"
```

### Update Registry:
```bash
python -c "
import json
from pathlib import Path

registry = json.load(open('models/llm/llm_registry.json'))
downloaded = []
for f in Path('models/llm').glob('*.gguf'):
    size_gb = f.stat().st_size / (1024**3)
    downloaded.append({'name': f.stem, 'size_gb': size_gb})

registry['downloaded'] = downloaded
json.dump(registry, open('models/llm/llm_registry.json', 'w'), indent=2)
print(f'Updated: {len(downloaded)} models')
"
```

### Test Sistem:
```bash
python kuera_ultimate_chat.py
```

---

## GUNAKAN SEKARANG (2 Models Ready)

Sementara menunggu download lengkap, Anda bisa menggunakan 2 model yang sudah ada:

```bash
python kuera_smart_chat.py
```

Command:
```
load TinyLlama-1.1B-Chat
Hello, who are you?
```

---

## TROUBLESHOOTING

### Error: "Repository Not Found"
- Pastikan nama repo benar
- Beberapa model mungkin private/removed

### Error: "No Space Left"
- Pastikan ada minimal 10 GB free space
- Hapus model yang tidak perlu

### Download Terputus
- Gunakan `resume_download=True` (otomatis)
- Atau download ulang dengan koneksi stabil

### Lambat
- Gunakan koneksi WiFi/Ethernet (bukan mobile)
- Download di malam hari (traffic rendah)
- Gunakan VPN jika HuggingFace diblokir

---

## KONTAK & SUPPORT

Jika ada masalah:
1. Cek dokumentasi: KUWERA_ULTIMATE_INTEGRATION.md
2. Cek status: python kuera_multi_model_manager.py
3. Restart download dengan: python download_auto.py

---

**Catatan**: Download 8 model memang membutuhkan waktu lama (2-4 jam) dan ruang besar (8.4 GB). Silakan download sesuai kebutuhan, Prioritas #1 adalah Qwen2.5-3B untuk Bahasa Indonesia terbaik.
