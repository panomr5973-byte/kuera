# Terabox Upload untuk KUERA

Script upload file-file besar KUERA ke cloud Terabox (akun: panomr5973@gmail.com).

## File yang Perlu Di-backup

| File/Folder | Ukuran | Prioritas |
|-------------|--------|-----------|
| `models/llm/*.gguf` | ~25 GB | TINGGI (model AI) |
| `data/kuera_database.db` | ~2.3 GB | TINGGI (database utama) |
| `data/international_data.db` | ~70 KB | SEDANG |
| `data/worldbank_indonesia.db` | ~80 KB | SEDANG |
| `data/kuera_evolution.db` | ~30 KB | RENDAH |

Total: ~27 GB (muat di Terabox free 1TB).

## Cara Ambil Cookies dari Browser

### 1. Login ke Terabox Web
1. Buka browser (Chrome/Edge)
2. Kunjungi: https://www.terabox.com
3. Login dengan akun **panomr5973@gmail.com**

### 2. Ambil Cookie `ndus` (PENTING!)

#### Metode A: Extension Cookie-Editor (Mudah)
1. Install extension **Cookie-Editor** di Chrome
2. Buka https://www.terabox.com (pastikan sudah login)
3. Klik icon Cookie-Editor di toolbar
4. Cari cookie bernama `ndus`
5. Copy value-nya
6. Paste ke file `cookies.json`

#### Metode B: DevTools (Manual)
1. Tekan `F12` → tab **Application** (Chrome) atau **Storage** (Firefox)
2. Di sidebar kiri: **Cookies** → `https://www.terabox.com`
3. Cari cookie bernama `ndus`
4. Copy value-nya

#### Metode C: Console (Cepat)
1. Tekan `F12` → tab **Console**
2. Paste kode ini lalu Enter:
   ```javascript
   console.log(document.cookie.split(';').find(c => c.trim().startsWith('ndus=')).split('=')[1]);
   ```
3. Copy outputnya

### 3. Ambil `jsToken` (Opsional tapi Direkomendasikan)
1. Di tab **Console**, paste:
   ```javascript
   console.log(require('system-core:context/context.js').instanceForSystem.jsToken);
   ```
   Atau cari di Network tab → XHR → lihat payload request → copy `jsToken`.

### 4. Isi `cookies.json`

Buka file `scripts/terabox/cookies.json` dan isi:

```json
{
    "ndus": "PASTE_NDUS_VALUE_DISINI",
    "csrfToken": "PASTE_CSRF_DISINI",
    "browserid": "PASTE_BROWSERID_DISINI",
    "lang": "en",
    "ndut_fmt": "PASTE_NDUT_FMT_DISINI"
}
```

> **Catatan:** Kalau sulit cari semua cookie, yang **paling penting** adalah `ndus`. Sisanya opsional.

## Cara Upload

### Upload Satu File
```bash
cd scripts/terabox
python upload.py --file "../../models/llm/gemma-2-2b-it-Q5_K_M.gguf" --remote "/KUERA_Backup/models/"
```

### Upload Semua Model
```bash
cd scripts/terabox
python upload.py --folder "../../models/llm" --remote "/KUERA_Backup/models/" --pattern "*.gguf"
```

### Upload Database
```bash
cd scripts/terabox
python upload.py --file "../../data/kuera_database.db" --remote "/KUERA_Backup/data/"
```

### Upload Semua File Penting (Batch)
```bash
cd scripts/terabox
python upload.py --batch batch_list.json
```

### Upload dengan Progress Bar
```bash
cd scripts/terabox
python upload.py --folder "../../models/llm" --remote "/KUERA_Backup/models/" --progress
```

## Archive & Split (Untuk File > 4GB)

Kadang upload file > 4GB lewat web/API bermasalah. Solusi: split jadi part.

### Buat Archive Terpisah
```bash
cd scripts/terabox
python archive_split.py --source "../../models/llm" --output "../../backup" --size 1900
```

Ini akan buat file `.7z.001`, `.7z.002`, dst, masing-masing ~1.9GB.
Lalu upload part-partnya:
```bash
python upload.py --folder "../../backup" --remote "/KUERA_Backup/models_archive/"
```

## Troubleshooting

### "Login Required" / 401 Unauthorized
- Cookie `ndus` expired. Login ulang di browser dan ambil cookie baru.
- Cookie `ndus` biasanya expired dalam beberapa jam.

### Upload Stuck / Slow
- Terabox throttling upload speed untuk free user (~1-3 MB/s).
- Coba upload malam hari atau pagi dini hari.
- File > 2GB lebih baik di-split dulu.

### File Not Found di Terabox
- Cek folder `/KUERA_Backup/` di web Terabox.
- Kadang upload berhasil tapi tidak muncul, refresh halaman.

### Tidak Bisa Upload File Besar
- Gunakan `archive_split.py` untuk split file jadi part 1.9GB.

## Keamanan

- **JANGAN** commit `cookies.json` ke GitHub! Sudah di-`.gitignore`.
- Cookie `ndus` seperti password — jangan share ke siapapun.
- Script ini hanya upload, tidak download atau delete file.
