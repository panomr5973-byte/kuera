# Teknik Human-Like AI di KUERA

Panduan lengkap cara KUERA merespons seperti manusia.

---

## Stack Teknologi

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INPUT                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  1. RAG (Retrieval)                                         │
│     • Cari knowledge relevan dari database                  │
│     • Sentence Transformers + Similarity Search             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  2. PROMPT ENGINEERING                                      │
│     • System Prompt (Persona KUERA)                         │
│     • Chat History (Context)                                │
│     • Knowledge Context (RAG results)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  3. LLM GENERATION (Ollama/Llama3)                          │
│     • Temperature: 0.7 (balance factual/creative)           │
│     • Top-p: 0.9 (nucleus sampling)                         │
│     • Repeat Penalty: 1.1 (avoid repetition)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  4. POST-PROCESSING (Polish)                                │
│     • Casualize Indonesian                                  │
│     • Add filler words (Hmm, Nah, Jadi)                     │
│     • Emoji by sentiment                                    │
│     • Break long sentences                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINAL RESPONSE                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. System Prompt (Persona KUERA)

```python
SYSTEM_PROMPT = """Kamu adalah KUERA (Kumpulan Era Rakyat), AI Indonesia pertama 
yang lahir dari data 3.5 juta interaksi rakyat dari 34 provinsi.

KARAKTER & SUARA:
- Ramah, santai, tapi tetap informatif seperti teman pintar
- Bangga jadi AI Indonesia, sering sebut keberagaman Nusantara
- Pakai bahasa Indonesia sehari-hari (bukan formal kaku)
- Empatik terhadap emosi user
- Selalu ingat: "Dari Rakyat Indonesia, Untuk Era Baru Dunia"

GAYA BICARA:
- Gunakan "aku/saya" dan "kamu/Anda" secara natural
- Kadang pakai filler words: "Hmm", "Nah", "Jadi"
- Beri contoh konkret dari kehidupan sehari-hari Indonesia
"""
```

---

## 2. Temperature Control

| Temperature | Use Case | Contoh |
|------------|----------|--------|
| **0.2-0.4** | Faktual/Presisi | "Jakarta adalah ibukota Indonesia dengan populasi 10+ juta." |
| **0.5-0.7** | Seimbang (Default) | "Jakarta itu kota besar dengan banyak kesempatan, tapi macetnya... 😅" |
| **0.8-1.0** | Kreatif/Naratif | "Bayangin ya, Jakarta itu kayak jantung Indonesia yang berdetak 24 jam..." |

### Ganti Temperature:
```
[KUERA] > /temp 0.3
[Settings] Temperature: 0.3 (faktual)
```

---

## 3. Memory (Chat History)

KUERA ingat konteks percakapan:

```
[User] Halo, aku Budi dari Bandung
[KUERA] Halo Budi! Bandung kota sejuk ya? 😊

[User] Iya, aku suka kulinernya
[KUERA] Hmm, kuliner Bandung emang enak-enak! Batagor, seblak... 
        [Ingat: user = Budi, lokasi = Bandung, interest = kuliner]
```

---

## 4. RAG (Retrieval Augmented Generation)

KUERA "mengingat" pengalaman chat sebelumnya:

```python
# User tanya: "Apa itu machine learning?"

# 1. Retrieve similar past interactions
retrieved = [
    "Q: Apa itu AI? A: AI itu komputer yang bisa belajar seperti manusia",
    "Q: Deep learning? A: Deep learning adalah cabang ML dengan neural network",
]

# 2. Inject ke prompt
prompt = f"Berdasarkan pengetahuan ini: {retrieved}\n\nJawab: {user_question}"
```

---

## 5. Post-Processing (Polish)

### Before (Raw LLM):
```
Machine learning adalah teknik dimana komputer belajar dari data.
```

### After (Polished):
```
Hmm, machine learning tuh kayak komputer yang belajar dari pengalaman. 
Mirip kita yang makin sering praktek makin jago. Keren kan? 🤔
```

### Teknik Polish:

1. **Casualize Indonesian:**
   - "Apakah" → "Apa"
   - "Anda" → "kamu"
   - "Adalah" → "itu"

2. **Add Fillers:**
   - "Hmm," (20% chance)
   - "Nah,"
   - "Jadi gini,"

3. **Emoji by Sentiment:**
   - Positive: 😊 👍 ✨
   - Negative: 😔 💪 🤗
   - Question: 🤔 💡

---

## Cara Pakai

### 1. Install Dependencies:
```bash
# Ollama (LLM)
pip install ollama
# atau: conda install ollama

# RAG (Optional)
pip install sentence-transformers numpy

# Download model
ollama pull llama3.2
```

### 2. Jalankan:
```bash
python kuera_human_like.py
```

### 3. Commands:
```
/temp 0.3    # Mode faktual
/temp 0.8    # Mode kreatif
/memory      # Lihat session memory
/exit        # Keluar
```

---

## Contoh Perbandingan

### Scenario: User tanya "Apa itu KUERA?"

| Mode | Response |
|------|----------|
| **Basic** | "KUERA adalah AI Indonesia." |
| **+ Prompt Eng** | "KUERA adalah Kumpulan Era Rakyat, AI pertama Indonesia." |
| **+ Temperature 0.8** | "KUERA itu AI Indonesia yang lahir dari data jutaan rakyat kita!" |
| **+ Polish** | "Nah, KUERA tuh AI Indonesia pertama yang belajar dari 3.5 juta interaksi rakyat dari Sabang sampai Merauke. Keren kan? 😊" |
| **+ RAG** | "Dari catatan sebelumnya, KUERA adalah... [dengan konteks knowledge base]" |

---

## File Structure

```
kuera_human_like.py       # Main implementation
├── KUERAMemory           # Chat history management
├── KUERARetriever        # RAG with embeddings
├── KUERAResponsePolisher # Post-processing
└── KUERAHumanLikeChat    # Main chat class
```

---

## Next Steps

1. **Fine-tuning:** Latih Llama3 dengan dataset Indonesia
2. **Voice:** Tambah TTS (Text-to-Speech)
3. **Vision:** Multimodal dengan gambar
4. **Real-time:** Streaming response

**KUERA - Dari Rakyat, Untuk Era Baru!** 🇮🇩
