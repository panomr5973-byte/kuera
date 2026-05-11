#!/usr/bin/env python
"""
KUWERA World Bank Setup
Setup lengkap untuk integrasi World Bank dengan AI Kuera
"""

import sys
import subprocess
from pathlib import Path


def print_header(title):
    print("="*70)
    print(title.center(70))
    print("="*70)


def check_dependencies():
    """Cek dan install dependencies"""
    print_header("CHECKING DEPENDENCIES")
    
    required = ['requests', 'pandas', 'numpy', 'sklearn']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"[OK] {pkg}")
        except ImportError:
            missing.append(pkg)
            print(f"[MISSING] {pkg}")
    
    if missing:
        print(f"\n[MENGINSTALL] {', '.join(missing)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("[OK] Dependencies installed")
    else:
        print("\n[OK] All dependencies available")


def step_1_fetch_data():
    """Step 1: Fetch data dari World Bank"""
    print_header("STEP 1: FETCH DATA WORLD BANK")
    
    try:
        import kuera_worldbank_integration as wb_integ
        wb_integ.main()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        return False


def step_2_train_model():
    """Step 2: Train model dengan data World Bank"""
    print_header("STEP 2: TRAIN ECONOMIC MODEL")
    
    try:
        import kuera_worldbank_trainer as wb_train
        wb_train.train_and_save()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to train model: {e}")
        return False


def step_3_test_chat():
    """Step 3: Test chat dengan data World Bank"""
    print_header("STEP 3: TEST WORLD BANK CHAT")
    
    try:
        from kuera_worldbank_chat import WorldBankChat
        
        chat = WorldBankChat()
        
        print("\n[Testing] Analisis ekonomi...")
        response = chat.process_query("Analisis kondisi ekonomi Indonesia")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        print("\n[Testing] Prediksi ekonomi...")
        response = chat.process_query("Prediksi prospek ekonomi")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        print("\n[OK] Chat system ready!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to test chat: {e}")
        return False


def create_readme():
    """Buat file README untuk dokumentasi"""
    readme_content = """# KUWERA World Bank Integration

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
"""
    
    with open('KUERA_WORLDBANK_README.md', 'w') as f:
        f.write(readme_content)
    
    print("[OK] README created: KUERA_WORLDBANK_README.md")


def main():
    """Main setup process"""
    print_header("KUWERA WORLD BANK SETUP")
    print("Integrasi data ekonomi World Bank dengan AI Kuera")
    print("="*70)
    
    # Check dependencies
    check_dependencies()
    
    # Step 1: Fetch data
    if not step_1_fetch_data():
        print("\n[FAILED] Setup aborted at Step 1")
        return
    
    # Step 2: Train model
    if not step_2_train_model():
        print("\n[WARNING] Model training failed, continuing...")
    
    # Step 3: Test chat
    if not step_3_test_chat():
        print("\n[WARNING] Chat test failed, continuing...")
    
    # Create README
    create_readme()
    
    # Summary
    print_header("SETUP COMPLETE!")
    print("""
KUWERA World Bank Integration telah siap!

File yang dibuat:
  - kuera_worldbank_integration.py  (Data fetcher)
  - kuera_worldbank_trainer.py      (ML trainer)
  - kuera_worldbank_chat.py         (Chat interface)
  - data/worldbank_indonesia.db     (Database)
  - models/worldbank/               (Trained models)

Cara menggunakan:
  1. Chat interaktif:
     python kuera_worldbank_chat.py

  2. Update data terbaru:
     python kuera_worldbank_integration.py

  3. Retrain model:
     python kuera_worldbank_trainer.py

Selamat menggunakan KUWERA dengan data ekonomi Indonesia! 🇮🇩
""")


if __name__ == "__main__":
    main()
