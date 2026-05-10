# KUWERA World Bank Integration

Integrasi data World Bank untuk AI Kuera - Analisis ekonomi Indonesia.

## Fitur

- **Data Ekonomi Real-time**: Mengambil data terbaru dari World Bank API
- **Analisis Komprehensif**: GDP, inflasi, pengangguran, kemiskinan, perdagangan
- **Prediksi Ekonomi**: Machine learning untuk prediksi kondisi ekonomi
- **Chat Interface**: Tanya jawab tentang ekonomi Indonesia

## Struktur File

| File | Fungsi |
|------|--------|
| `kuera_worldbank_integration.py` | Fetch dan simpan data World Bank |
| `kuera_worldbank_trainer.py` | Train model ML dengan data ekonomi |
| `kuera_worldbank_chat.py` | Chat interface untuk analisis ekonomi |
| `kuera_worldbank_setup.py` | Setup lengkap (file ini) |

## Cara Penggunaan

### 1. Setup Lengkap
```bash
python kuera_worldbank_setup.py
```

### 2. Fetch Data World Bank
```bash
python kuera_worldbank_integration.py
```

### 3. Train Model
```bash
python kuera_worldbank_trainer.py
```

### 4. Chat dengan AI
```bash
python kuera_worldbank_chat.py
```

## Indikator Ekonomi yang Tersedia

### Ekonomi Makro
- GDP (current US$)
- GDP growth (annual %)
- GDP per capita
- Inflation (consumer prices)

### Perdagangan
- Exports of goods and services
- Imports of goods and services

### Ketenagakerjaan
- Unemployment rate
- Employment to population ratio

### Sosial
- Poverty headcount ratio
- GINI index

### Pendidikan
- School enrollment, primary
- School enrollment, secondary
- School enrollment, tertiary

### Kesehatan
- Life expectancy at birth
- Mortality rate, under-5

### Infrastruktur
- Internet users (% of population)
- Access to electricity

### Lingkungan
- CO2 emissions
- Forest area

### Demografi
- Population, total
- Urban population

## Contoh Pertanyaan untuk Chat

- "Analisis kondisi ekonomi Indonesia"
- "Prediksi prospek ekonomi"
- "Bandingkan dengan negara tetangga"
- "Data GDP 5 tahun terakhir"
- "Bagaimana inflasi saat ini?"

## Database

Data disimpan di `data/worldbank_indonesia.db` dengan tabel:
- `worldbank_indicators`: Data indikator historis
- `indicator_metadata`: Metadata indikator
- `worldbank_training`: Data untuk training ML

## Model

Model ML disimpan di `models/worldbank/`:
- Model prediksi kondisi ekonomi (baik/perlu perhatian)
- Menggunakan Random Forest, Gradient Boosting, Logistic Regression
- Ensemble model untuk akurasi terbaik

## API World Bank

Data diambil dari: https://api.worldbank.org/v2

Untuk Indonesia (kode negara: IDN)

---

**KUWERA** - AI berjiwa Indonesia dengan data ekonomi real-time
