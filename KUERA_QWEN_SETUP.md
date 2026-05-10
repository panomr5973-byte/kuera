# KUWERA QWEN Integration Guide

## Status: Model Downloaded ✅

Model Qwen2.5-1.5B-Instruct (1.04 GB) berhasil didownload!

---

## Metode Integrasi

### Opsi 1: Menggunakan Ollama (Recommended)

Ollama adalah cara termudah untuk menjalankan model GGUF.

```bash
# 1. Install Ollama (download dari https://ollama.com)
# 2. Buat Modelfile
```

**Modelfile**:
```dockerfile
FROM ./models/llm/qwen2.5-1.5b-instruct-q4_k_m.gguf

TEMPLATE """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
"""

SYSTEM """Kamu adalah Kuwera, AI asisten cerdas dari Indonesia. 
Jawablah dalam Bahasa Indonesia yang baik dan benar."""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
```

**Jalankan**:
```bash
ollama create kuera-qwen -f Modelfile
ollama run kuera-qwen
```

---

### Opsi 2: Menggunakan llamafile (Single Executable)

llamafile adalah executable tunggal yang berisi model + runtime.

```bash
# Download llamafile
wget https://github.com/Mozilla-Ocho/llamafile/releases/download/0.8.4/llamafile-0.8.4

# Jalankan dengan model Qwen
./llamafile-0.8.4 -m models/llm/qwen2.5-1.5b-instruct-q4_k_m.gguf \
  --host 0.0.0.0 --port 8080
```

---

### Opsi 3: Menggunakan llama-cpp-python (Pre-built)

```bash
# Install pre-built wheel (Windows)
pip install llama-cpp-python --no-cache-dir

# Jika gagal, gunakan wheel spesifik
pip install https://github.com/abetlen/llama-cpp-python/releases/download/v0.2.90/llama_cpp_python-0.2.90-cp311-cp311-win_amd64.whl
```

**Python Code**:
```python
from llama_cpp import Llama

model = Llama(
    model_path="models/llm/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    n_ctx=2048,
    verbose=False
)

# Chat dengan format Qwen
prompt = """<|im_start|>system
Kamu adalah Kuwera, AI asisten Indonesia.<|im_end|>
<|im_start|>user
Halo!<|im_end|>
<|im_start|>assistant
"""

output = model(prompt, max_tokens=100)
print(output['choices'][0]['text'])
```

---

### Opsi 4: Menggunakan HuggingFace Transformers

```bash
pip install transformers accelerate
```

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-1.5B-Instruct"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Chat
messages = [
    {"role": "system", "content": "Kamu adalah Kuwera, AI asisten Indonesia."},
    {"role": "user", "content": "Halo, siapa kamu?"}
]

text = tokenizer.apply_chat_template(messages, tokenize=False)
inputs = tokenizer(text, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0]))
```

---

## Format Chat Qwen

Qwen menggunakan format khusus:

```
<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{user_message}<|im_end|>
<|im_start|>assistant
{assistant_response}<|im_end|>
```

**Contoh**:
```
<|im_start|>system
Kamu adalah Kuwera, AI asisten Indonesia.<|im_end|>
<|im_start|>user
Apa itu AI?<|im_end|>
<|im_start|>assistant
AI adalah kecerdasan buatan yang...
```

---

## Integrasi dengan Kuera

Setelah model berjalan, integrasikan dengan Kuera:

```python
# kuera_qwen_integration.py
import requests

class QwenAPI:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def chat(self, message: str) -> str:
        response = requests.post(f"{self.base_url}/api/generate", json={
            "model": "kuera-qwen",
            "prompt": message,
            "stream": False
        })
        return response.json()['response']

# Gunakan dalam Smart Chat
from kuera_smart_chat import SmartChat

class EnhancedSmartChat(SmartChat):
    def __init__(self):
        super().__init__()
        self.qwen_api = QwenAPI()
    
    def generate_llm_response(self, message: str) -> str:
        # Gunakan Qwen via Ollama API
        return self.qwen_api.chat(message)
```

---

## Status Integrasi

| Komponen | Status |
|----------|--------|
| Model Downloaded | ✅ 1.04 GB |
| Registry Updated | ✅ |
| CTransformers | ❌ (tidak support) |
| Ollama Ready | ✅ (dapat digunakan) |
| llamafile Ready | ✅ (dapat digunakan) |
| HF Transformers | ✅ (dapat digunakan) |

---

## Rekomendasi

**Untuk Pengguna Windows**: Gunakan **Ollama** (paling mudah)
**Untuk Developer**: Gunakan **HF Transformers** (paling fleksibel)
**Untuk Deployment**: Gunakan **llamafile** (portable)

---

## Next Steps

1. Install Ollama dari https://ollama.com
2. Buat Modelfile (lihat di atas)
3. Jalankan: `ollama create kuera-qwen -f Modelfile`
4. Integrasikan dengan Kuera Smart Chat

Model Qwen sudah siap digunakan untuk Bahasa Indonesia! 🇮🇩
