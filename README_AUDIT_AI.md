# 🤖 AI Audit Toolkit untuk Government Audit Agency

Toolkit analisis data untuk pendukung audit Government Audit Agency dengan Python.

## 📦 Daftar File

| File | Deskripsi |
|------|-----------|
| `audit_toolkit.py` | Audit Keuangan Lengkap (Excel + Anomaly + Filter + Viz + PDF) |
| `template_audit_spi.py` | Audit SPI berbasis COSO Framework |
| `template_audit_kinerja.py` | Audit Kinerja dengan Scoring & Ranking |
| `template_master.py` | Menu utama integrasi semua audit (CLI) |
| `src/data/audit_workflow.py` | Unified orchestrator untuk semua jenis audit |
| `src/web/dashboard.py` | Web UI dengan tab Audit Workflow |

## 🚀 Cara Menggunakan

### Opsi 1: Web Dashboard (Recommended)
Jalankan KUERA Control Panel:
```bash
python main.py
```
Buka `http://localhost:7777` → Tab **Audit Workflow**
- Upload file Excel
- Pilih jenis audit (Keuangan / SPI / Kinerja)
- Klik "Jalankan Audit"
- Lihat hasil analisis & download laporan

### Opsi 2: Menu Interaktif (CLI)
```bash
python template_master.py
```

### Opsi 3: Langsung Jalankan
```bash
# Audit Keuangan
python template_master.py keuangan

# Audit SPI
python template_master.py spi

# Audit Kinerja
python template_master.py kinerja

# Lihat contoh kode
python template_master.py contoh
```

### Opsi 4: Import di Script Python
```python
from audit_toolkit import ExcelAuditProcessorV2, BUMDAnalyzer

proc = ExcelAuditProcessorV2()
df = proc.read_excel_multiheader('data.xlsx', [0, 1])
proc.detect_and_convert_numbers(df)
proc.calculate_financial_ratios(df)

# Anomaly detection (IQR + Z-Score + Benford's Law)
anomalies = proc.detect_anomalies(df)

analyzer = BUMDAnalyzer(df)
low_roa = analyzer.filter_by_roa(max_roa=5)
```

### Opsi 5: API Endpoints
```bash
# List available templates
curl http://localhost:7777/api/audit/templates

# Upload file
curl -X POST -F "file=@data.xlsx" http://localhost:7777/api/audit/upload

# Run audit
curl -X POST http://localhost:7777/api/audit/run \
  -H "Content-Type: application/json" \
  -d '{"jenis":"keuangan","filename":"data.xlsx"}'
```

## 📋 Format File Input

### Audit Keuangan
File Excel dengan multi-header (2 baris):
- Baris 1: Kategori (Total Aset, Total Kewajiban, dll)
- Baris 2: Tahun (2020, 2021, 2022, dll)
- Kolom wajib: ID BUMD, Nama BUMD

### Audit SPI
File Excel dengan kolom:
- `komponen`: Kode komponen (LINGKUNGAN_PENGENDALIAN, PENILAIAN_RISIKO, dll)
- `indikator`: Nama indikator
- `nilai`: 1-5 (1=Sangat Lemah, 5=Sangat Baik)
- `keterangan`: Catatan (opsional)

### Audit Kinerja
File Excel dengan kolom indikator:
- `nama`: Nama entitas
- `realisasi_anggaran`, `efisiensi_biaya`, `kemandirian`
- `kepuasan_pelanggan`, `waktu_pelayanan`, `keluhan_terselesaikan`
- `volume_produksi`, `kualitas_output`, `penggunaan_kapasitas`
- `disiplin_pegawai`, `pengembangan_kompetensi`, `pengurangan_turnover`

## 📁 Output File

### Audit Keuangan
- `hasil_audit_keuangan.xlsx` - Data lengkap dengan filter
- `roa_dist.png` - Grafik distribusi ROA
- `aset_trend.png` - Grafik tren aset
- `laporan_keuangan.pdf` - Laporan PDF

### Audit SPI
- `hasil_audit_spi.xlsx` - Ringkasan, detail, rekomendasi

### Audit Kinerja
- `hasil_audit_kinerja.xlsx` - Ranking, Top 10, Bottom 10, Distribusi
- `kinerja_distribusi.png` - Histogram skor
- `kinerja_predikat.png` - Pie chart predikat
- `kinerja_top10.png` - Bar chart top 10

## 🔧 Instalasi Requirements

```bash
pip install pandas numpy matplotlib seaborn openpyxl fpdf
```

## 💡 Tips Penggunaan

1. **Backup Model**: Model LightGBM Anda tersimpan di `D:\AI-Backup-2026\models\`
2. **Virtual Environment**: Selalu aktifkan venv sebelum menjalankan:
   ```bash
   source ~/ai-audit/venv/bin/activate  # WSL
   # atau
   .\venv\Scripts\activate  # Windows
   ```
3. **Data Sensitif**: Jangan upload file klien ke cloud, proses semua di lokal.

## 📞 Troubleshooting

### Error "File not found"
Pastikan file Excel ada di folder yang sama dengan script, atau berikan path lengkap.

### Error "Module not found"
Install requirements:
```bash
pip install pandas numpy matplotlib openpyxl fpdf
```

### Error "Permission denied" (WSL)
Pastikan file memiliki permission execute:
```bash
chmod +x *.py
```

## 🏗️ Arsitektur

```
AI Audit Toolkit
├── ExcelProcessorV2    (Baca & bersihkan data Excel)
├── BUMDAnalyzer        (Filter & identifikasi)
├── AuditVisualizer     (Grafik & chart)
├── PDFReport           (Generate laporan PDF)
├── AuditSPI            (Evaluasi COSO)
└── AuditKinerja        (Scoring & ranking)
```

## 👤 Author
Dibuat untuk: **panomr (Government Audit Agency)**  
Tanggal: April 2026
