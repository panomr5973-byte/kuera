# KUERA Chat Interface

Interface chat interaktif untuk KUERA AI Indonesia.

---

## Cara Pakai

### 1. Chat Sederhana (Recommended)
```powershell
python kuera_chat_simple.py
```

### 2. Chat Lengkap (Dengan Intent Recognition)
```powershell
python kuera_chat_improved.py
```

### 3. Chat dengan Database
```powershell
python kuera_chat.py
```

---

## Contoh Percakapan

```
======================================================================
                    KUERA CHAT
======================================================================

  AI Indonesia - Dari Rakyat, Untuk Era Baru
  Data: 3.5M interaksi | 34 Provinsi | 277 juta rakyat

  Perintah: help, info, stats, exit
======================================================================

Nama Anda: User

[KUERA] Halo User! Mari berkenalan.
[KUERA] Saya KUERA, AI dari rakyat Indonesia. Ketik 'help' untuk bantuan.

[User] halo
[KUERA] Halo User! Saya KUERA, AI dari rakyat Indonesia. Ada yang bisa saya bantu?

[User] siapa kamu
[KUERA] Nama saya KUERA (Kumpulan Era Rakyat). Saya adalah AI Indonesia pertama 
        yang lahir dari data 3.5 juta interaksi rakyat dari 34 provinsi. 
        Dari Rakyat Indonesia, Untuk Era Baru Dunia.

[User] apa itu kuera
[KUERA] KUERA adalah AI Indonesia yang belajar dari keberagaman rakyat Indonesia. 
        Saya dilatih dengan 3,502,258 interaksi dari 34 provinsi. 
        Saya memahami bahasa Indonesia, emosi, dan konteks lokal.

[User] indonesia
[KUERA] Indonesia adalah negara kepulauan terbesar dengan 17.000+ pulau, 
        277 juta penduduk, 34 provinsi, dan 1,300+ suku bangsa. 
        Kekayaan kita bukan hanya sumber daya alam, tapi juga keberagaman budaya!

[User] terima kasih
[KUERA] Sama-sama! Senang bisa membantu rakyat Indonesia.

[User] exit
[KUERA] Terima kasih User! Sampai jumpa.
        Ingat: KUERA terus belajar dari rakyat Indonesia.
        Dari Sabang sampai Merauke - Indonesia Maju!
```

---

## Intent Recognition

KUERA mengenali intent berikut:

| Intent | Contoh Input |
|--------|-------------|
| greeting | halo, hai, hello |
| identity | siapa kamu, nama anda |
| what_is_kuera | apa itu kuera |
| capabilities | bisa apa, fitur |
| indonesia | tentang indonesia |
| gratitude | terima kasih, makasih |
| negative_emotion | sedih, cemas, takut |
| help | help, bantuan |
| info | info, tentang |
| stats | stats, statistik |

---

## Perintah Tersedia

| Command | Fungsi |
|---------|--------|
| help | Tampilkan bantuan |
| info | Info tentang KUERA |
| stats | Statistik session |
| exit / quit / keluar | Keluar dari chat |

---

## Files

| File | Deskripsi |
|------|-----------|
| `kuera_chat_simple.py` | Chat sederhana |
| `kuera_chat_improved.py` | Chat dengan intent recognition |
| `kuera_chat.py` | Chat dengan database integration |
