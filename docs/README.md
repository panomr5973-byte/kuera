# KUERA AI Project - Documentation

Complete AI/ML project structure with comprehensive tooling for data processing, model training, evaluation, and deployment.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
- [Quick Start Guide](#quick-start-guide)
- [Configuration](#configuration)
- [Next Steps](#next-steps)
- [Support](#support)

---

## Overview

KUERA (EraKu) adalah AI Indonesia yang lahir dari data lengkap 34 provinsi. Proyek ini menyediakan infrastruktur lengkap untuk pengembangan AI/ML dengan fitur:

- **Dual-Drive Workspace**: Optimasi penyimpanan C: (System) dan D: (Archive)
- **Database Integration**: SQLite local dengan opsi migrasi ke cloud
- **Multi-Model Training**: Training dan evaluasi multiple ML models
- **Interactive Dashboard**: Streamlit dashboard untuk visualisasi dan prediksi
- **MLOps Ready**: MLflow tracking, monitoring, dan deployment tools

### Project Structure

```
AI-Project/
├── ai_env/                 # Virtual environment
├── config/                 # Path configuration
├── data/
│   ├── raw/               # Raw data
│   ├── processed/         # Cleaned data
│   └── external/          # External data sources
├── notebooks/             # Jupyter notebooks
├── src/
│   ├── data/              # Data processing scripts
│   ├── models/            # Model training scripts
│   ├── evaluation/        # Evaluation scripts
│   └── deployment/        # Deployment scripts
├── models/                # Saved models (.pkl, .pt, .onnx)
├── app/                   # Streamlit/FastAPI applications
├── monitoring/            # Disk monitoring & dashboard
├── scripts/               # Maintenance & sync scripts
├── logs/                  # Training & monitoring logs
└── requirements.txt       # Dependencies
```

---

## System Requirements

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Storage C: | 50 GB free | 100 GB free |
| Storage D: | 100 GB free | 200 GB free |
| RAM | 8 GB | 16 GB+ |
| CPU | 4 cores | 8 cores+ |

### Software Requirements

- **OS**: Windows 10/11, Linux, atau macOS
- **Python**: 3.10+ (current: 3.14.3)
- **Virtual Environment**: `ai_env` (auto-created)

### Installed Libraries

#### 🤖 Deep Learning & AI
| Library | Versi | Fungsi |
|---------|-------|--------|
| PyTorch | 2.11.0+cpu | Deep learning framework |
| Transformers | 5.4.0 | Hugging Face models |
| Accelerate | 1.13.0 | Training optimization |
| Datasets | 4.8.4 | Dataset management |

#### 🧮 Machine Learning
| Library | Versi | Fungsi |
|---------|-------|--------|
| Scikit-learn | 1.8.0 | ML algorithms |
| XGBoost | 3.2.0 | Gradient boosting |
| LightGBM | 4.6.0 | Fast gradient boosting |
| SHAP | 0.51.0 | Model interpretability |

#### 📊 Data & Visualization
| Library | Versi | Fungsi |
|---------|-------|--------|
| Pandas | 2.3.3 | Data manipulation |
| NumPy | 2.4.4 | Numerical computing |
| Polars | 1.39.3 | Fast DataFrame |
| Matplotlib | 3.10.8 | Plotting |
| Seaborn | 0.13.2 | Statistical visualization |
| Plotly | 5.24.1 | Interactive plots |

#### 🚀 Deployment & MLOps
| Library | Versi | Fungsi |
|---------|-------|--------|
| FastAPI | 0.135.3 | REST API framework |
| Streamlit | 1.56.0 | Data apps |
| MLflow | 3.10.1 | Experiment tracking |
| Evidently | 0.7.21 | Data drift monitoring |
| ONNX | 1.21.0 | Model optimization |

---

## Installation Steps

### 1. Clone/Setup Project

```bash
cd D:\workspace\AI-Project
```

### 2. Activate Virtual Environment

```powershell
# Windows PowerShell
ai_env\Scripts\Activate.ps1

# atau
cd D:\workspace\AI-Project
.\ai_env\Scripts\Activate.ps1
```

### 3. Verify Environment

```bash
python verify_env.py
```

### 4. Setup Database (Opsional)

```powershell
# Setup database SQLite local
python kuera_setup_database.py
```

**Database Structure:**
- `interactions` - Chat history
- `user_profiles` - User profiles
- `model_metrics` - Performance metrics
- `knowledge_base` - RAG knowledge
- `sessions` - Session management
- `analytics_daily` - Daily statistics

---

## Quick Start Guide

### 🚀 3-Step Quick Start

#### Step 1: Data Pipeline
```bash
python src/data/pipeline.py
```

**Output:**
- `data/raw/sample_dataset.csv` - Sample dataset
- `data/processed/X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`
- `data/processed/pipeline_metadata.json`

#### Step 2: Training Model
```bash
python src/models/train_example.py
```

**Output:**
- `models/best_model_*.pkl` - Best model saved
- `models/model_metadata.json` - Evaluation results
- MLflow tracking (jika diaktifkan)

#### Step 3: Dashboard
```bash
streamlit run app/dashboard.py
```

Buka browser: http://localhost:8501

### 🎯 Run All Steps at Once

```bash
python run_pipeline.py --step all
```

### 💬 Chat Interface

#### Chat Sederhana (tanpa database)
```powershell
python kuera_chat_simple.py
```

#### Chat Lengkap (dengan database)
```powershell
python kuera_chat.py
```

### 📊 Monitoring & Services

```bash
# Check disk space
python monitoring\disk_monitor.py

# MLflow UI
mlflow ui

# Label Studio (data labeling)
label-studio start

# Daily maintenance
python scripts\daily_maintenance.py
```

---

## Configuration

### Path Configuration

Gunakan unified path management di `config/paths.py`:

```python
from config.paths import get_path, get_paths

# Get specific path
models_path = get_path("active_models")    # C:\AI-Project\models
backup_path = get_path("model_backup")     # D:\AI-Backup-2026\models

# Get all paths
paths = get_paths()
print(paths.model_archive)  # D:\AI-Models-Archive\models

# Ensure path exists
paths.ensure_exists(paths.model_backup)
```

### Workspace Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                      DRIVE C: (System)                          │
├─────────────────────────────────────────────────────────────────┤
│ C:\AI-Project\                                                  │
│ ├── 💻 Source Code                                              │
│ ├── 🤖 models\           → Active models                        │
│ ├── 🗃️ mlflow.db         → Experiment tracking                   │
│ └── 📊 config/           → Path management                       │
└─────────────────────────────────────────────────────────────────┘
                              ↕️  Auto-Sync Daily
┌─────────────────────────────────────────────────────────────────┐
│                    DRIVE D: (Data/Archive)                      │
├─────────────────────────────────────────────────────────────────┤
│ D:\AI-Backup-2026\      → Model backups                         │
│ D:\AI-Models-Archive\   → HF Models archive                     │
│ D:\DataKlien\           → Client data                            │
└─────────────────────────────────────────────────────────────────┘
```

### Auto-Sync Setup

```powershell
# Manual sync
python scripts\sync_models.py

# Setup scheduled task (Run as Administrator)
cd D:\workspace\AI-Project\scripts
powershell -ExecutionPolicy Bypass -File setup_scheduled_task.ps1
```

### Customization

#### Menggunakan Data Sendiri
```python
# Di src/data/pipeline.py
df = pd.read_csv('data/raw/data_anda.csv')

# Update config
pipeline.config['target_column'] = 'nama_target'
pipeline.config['categorical_columns'] = ['kolom1', 'kolom2']
```

#### Menambah Model
```python
# Di src/models/train_example.py
trainer.model_configs['my_model'] = {
    'model': MyCustomClassifier(),
    'params': {'param1': [1, 2, 3]}
}
```

---

## Next Steps

### Phase 1: Data Preparation
- [ ] Setup folder `data/raw/`, `data/processed/`
- [ ] Upload dataset
- [ ] Data cleaning dengan `src/data/preprocessing.py`
- [ ] Labeling dengan Label Studio (jika perlu)

### Phase 2: EDA
- [ ] Jupyter notebook untuk eksplorasi
- [ ] Visualisasi dengan Matplotlib/Seaborn
- [ ] Statistik deskriptif

### Phase 3: Model Development
- [ ] Feature engineering
- [ ] Training dengan `src/models/train.py`
- [ ] Hyperparameter tuning
- [ ] Experiment tracking dengan MLflow

### Phase 4: Evaluation
- [ ] Metrics dengan `src/evaluation/metrics.py`
- [ ] SHAP values untuk interpretability
- [ ] Confusion matrix, ROC curve

### Phase 5: Deployment
- [ ] Export model (ONNX/Joblib)
- [ ] Streamlit demo
- [ ] FastAPI serving
- [ ] Monitoring dengan Evidently

### Cloud Migration (Opsional)
1. **Test Local**: Jalankan `kuera_chat_simple.py`
2. **Setup Cloud**: Pilih provider (Supabase/PlanetScale/AWS RDS)
3. **Deploy**: Upload ke server/cloud
4. **Scale**: Tambah fitur AI yang lebih advanced

---

## Support

### Troubleshooting

#### Module Not Found
```bash
# Pastikan environment aktif
ai_env\Scripts\Activate.ps1

# Reinstall jika perlu
pip install -r requirements.txt
```

#### SSL Certificate Error
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>
```

#### Port 8501 sudah digunakan
```bash
# Ganti port
streamlit run app/dashboard.py --server.port 8502
```

#### File Not Found
```bash
# Jalankan pipeline data dulu
python src/data/pipeline.py
```

### Monitoring Resources

| Service | URL | Command |
|---------|-----|---------|
| Streamlit | http://localhost:8501 | `streamlit run app/dashboard.py` |
| MLflow UI | http://localhost:5000 | `mlflow ui` |
| Label Studio | http://localhost:8080 | `label-studio start` |
| FastAPI | http://localhost:8000 | `uvicorn app.api:app --reload` |

### Log Files
- Sync log: `logs/sync_history.json`
- Disk monitor: `logs/disk_monitor.json`

### Documentation & Resources
- **PyTorch**: https://pytorch.org/docs
- **Scikit-learn**: https://scikit-learn.org
- **Transformers**: https://huggingface.co/docs/transformers
- **MLflow**: https://mlflow.org/docs
- **Streamlit**: https://docs.streamlit.io
- **FastAPI**: https://fastapi.tiangolo.com

### File Penting

| File | Deskripsi |
|------|-----------|
| `src/data/pipeline.py` | Data processing pipeline lengkap |
| `src/models/train_example.py` | Training multiple models |
| `app/dashboard.py` | Streamlit dashboard interaktif |
| `run_pipeline.py` | Runner untuk semua steps |
| `verify_env.py` | Cek environment |
| `config/paths.py` | Path management |
| `monitoring/disk_monitor.py` | Disk space monitoring |

---

**Status**: ✅ Environment Siap untuk Pengembangan AI!

**Selamat! KUERA siap digunakan!** 🇮🇩🚀
