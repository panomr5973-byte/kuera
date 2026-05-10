# ☁️ Backup KUERA ke Terabox

Panduan cepat backup file-file besar KUERA ke cloud Terabox (akun: **panomr5973@gmail.com**).

## 📦 File yang Perlu Di-backup

| Item | Ukuran | Lokasi |
|------|--------|--------|
| Model LLM (.gguf) | ~25 GB | `models/llm/` |
| Database utama | ~2.3 GB | `data/kuera_database.db` |
| Database lainnya | ~200 KB | `data/*.db` |

**Total: ~27 GB** → muat di Terabox free (1 TB).

---

## 🔐 Langkah 1: Ambil Cookie dari Browser

1. Buka browser, kunjungi **https://www.terabox.com**
2. Login dengan akun **panomr5973@gmail.com**
3. Tekan `F12` → tab **Console**
4. Paste kode ini lalu Enter:
   ```javascript
   console.log(document.cookie.split(';').find(c => c.trim().startsWith('ndus=')).split('=')[1]);
   ```
5. Copy outputnya (string panjang)

> Kalau kode di atas error, coba: **F12 → Application → Cookies → https://www.terabox.com → cari `ndus` → copy value**

---

## 📝 Langkah 2: Isi Cookies

1. Buka file `scripts/terabox/cookies.json`
2. Ganti value `ndus` dengan cookie yang tadi dicopy:
   ```json
   {
       "ndus": "YxN...D5s",
       "lang": "en"
   }
   ```
3. Save

> **PENTING:** Jangan commit `cookies.json` ke GitHub! Sudah di-`.gitignore`.

---

## 🚀 Langkah 3: Upload

### Metode A: Batch File (Mudah)
```cmd
cd scripts\terabox
backup_all.bat
```
Pilih menu 1-5, script akan upload otomatis.

### Metode B: PowerShell (Cepat)
```powershell
cd scripts\terabox
.\quick_upload.ps1 -Type models    # Upload semua model
.\quick_upload.ps1 -Type database # Upload database utama
.\quick_upload.ps1 -Type all      # Upload semuanya
```

### Metode C: Python Langsung
```bash
cd scripts/terabox

# Test login dulu
python upload.py --file "../../data/kuera_database.db" --remote "/KUERA_Backup/test"

# Upload model
python upload.py --folder "../../models/llm" --remote "/KUERA_Backup/models" --pattern "*.gguf"

# Upload database
python upload.py --file "../../data/kuera_database.db" --remote "/KUERA_Backup/data"
```

---

## 📦 Upload File Besar (> 4GB)

Terabox kadang bermasalah dengan file > 4GB. Solusi: **split archive**.

```bash
cd scripts/terabox

# Split database 2.3GB jadi part ~1.9GB
python archive_split.py --source "../../data/kuera_database.db" --output "../../backup" --size 1900

# Upload part-partnya
python upload.py --folder "../../backup" --remote "/KUERA_Backup/data_archive"
```

> Butuh **7-Zip** terinstall: https://www.7-zip.org/download.html

---

## ⚠️ Troubleshooting

| Masalah | Solusi |
|---------|--------|
| "Login failed" / 401 | Cookie `ndus` expired. Login ulang di browser, ambil cookie baru. |
| Upload lambat | Normal untuk free user (~1-3 MB/s). Upload malam hari lebih cepat. |
| File > 4GB gagal | Gunakan `archive_split.py` untuk split jadi part 1.9GB. |
| `7z not found` | Install 7-Zip dan tambahkan ke PATH. |

---

## 📁 Struktur Folder di Terabox

Setelah upload, file akan tersusun di Terabox:
```
/KUERA_Backup/
├── models/
│   └── llm/
│       ├── gemma-2-2b-it-Q5_K_M.gguf
│       ├── Llama-3.2-3B-Instruct-Q4_K_M.gguf
│       └── ...
├── data/
│   ├── kuera_database.db
│   ├── international_data.db
│   └── worldbank_indonesia.db
└── logs/
    └── ...
```

---

## 🔒 Keamanan

- Cookie `ndus` = seperti password. **Jangan share ke siapapun.**
- File `cookies.json` sudah di-`.gitignore`, tidak akan masuk GitHub.
- Script hanya **upload**, tidak bisa download atau hapus file.
