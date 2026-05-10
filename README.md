# AI Project

Complete AI/ML project structure with comprehensive tooling for data processing, model training, evaluation, and deployment.

## 🎉 Installation Complete!

Your environment is ready with all necessary libraries installed.

## 📁 Project Structure

```
AI-Project/
├── ai_env/                 # Virtual environment (already activated)
├── data/
│   ├── raw/               # Raw data (don't modify)
│   ├── processed/         # Cleaned/processed data
│   └── external/          # External data sources
├── notebooks/             # Jupyter notebooks for exploration
├── src/
│   ├── data/              # Data processing scripts
│   ├── models/            # Model training scripts
│   ├── evaluation/        # Evaluation scripts
│   └── deployment/        # Deployment scripts
├── models/                # Saved models (.pkl, .pt, .onnx)
├── reports/               # Evaluation results & visualizations
├── app/                   # Streamlit/FastAPI applications
│   ├── app.py            # Streamlit UI
│   └── api.py            # FastAPI endpoints
├── logs/                  # Training & monitoring logs
├── verify_env.py         # Environment verification script
├── requirements.txt      # Dependencies
└── README.md             # This file
```

## ✅ Installed Libraries

### 🤖 Deep Learning & ML
- **PyTorch** (2.11.0+cpu) - Deep learning framework
- **Transformers** (5.4.0) - Hugging Face transformers
- **Accelerate** (1.13.0) - Training acceleration
- **Datasets** (4.8.4) - Dataset handling

### 🧮 Classical ML
- **Scikit-learn** (1.8.0) - ML algorithms & utilities
- **XGBoost** (3.2.0) - Gradient boosting
- **LightGBM** (4.6.0) - Fast gradient boosting

### 📊 Data Processing
- **Pandas** (2.3.3) - Data manipulation
- **NumPy** (2.4.4) - Numerical computing
- **PyArrow** (22.0.0) - Columnar data format

### 📈 Visualization & Evaluation
- **Matplotlib** (3.10.8) - Plotting
- **Seaborn** (0.13.2) - Statistical visualization
- **SHAP** (0.51.0) - Model interpretability
- **Statsmodels** (0.14.6) - Statistical models
- **Evidently** (0.7.21) - ML monitoring

### 🚀 Deployment
- **FastAPI** (0.135.3) - Web framework
- **Streamlit** (1.56.0) - Data apps
- **ONNX** (1.21.0) - Model optimization
- **MLflow** (3.10.1) - Experiment tracking

### 🔧 Utilities
- **Jupyter** (1.1.1) - Notebooks
- **OpenAI** (1.109.1) - OpenAI API
- **Label Studio** (1.23.0) - Data labeling

## 🚀 Quick Start

### 1. Verify Environment
```bash
python verify_env.py
```

### 2. Start Jupyter Notebook
```bash
jupyter notebook
```

### 3. Run Streamlit App
```bash
streamlit run app/app.py
```

### 4. Run FastAPI Server
```bash
python app/api.py
# or
uvicorn app.api:app --reload
```

### 5. Start Label Studio (for data labeling)
```bash
label-studio start
```

## 📖 Usage Examples

### Data Processing
```python
from src.data.preprocessing import load_data, clean_data

df = load_data('data/raw/mydata.csv')
df_clean = clean_data(df)
```

### Model Training
```python
from src.models.train import train_model

model = train_model('data/processed/train.csv', 'models/model.pkl')
```

### Evaluation
```python
from src.evaluation.metrics import plot_confusion_matrix

plot_confusion_matrix(y_true, y_pred, 'reports/confusion_matrix.png')
```

## 🛠️ Development Workflow

1. **Data Collection** → Place in `data/raw/`
2. **Exploration** → Use `notebooks/`
3. **Processing** → Use `src/data/`
4. **Training** → Use `src/models/`
5. **Evaluation** → Use `src/evaluation/`
6. **Deployment** → Use `app/`

## 🔍 Monitoring & Tracking

- **MLflow UI**: `mlflow ui` (access at http://localhost:5000)
- **Evidently**: Built-in data drift detection
- **Label Studio**: http://localhost:8080 (when running)

## 📝 Notes

- Virtual environment `ai_env` is already activated
- SQLite is built-in with Python (no separate install needed)
- PyTorch CPU version installed (no GPU required)
- All scripts have `.gitkeep` for empty folder tracking

## 🆘 Troubleshooting

### SSL Certificate Error
If you encounter SSL errors when installing packages:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>
```

### Label Studio Dependencies
Label Studio requires specific versions. If conflicts occur:
```bash
pip install label-studio --force-reinstall
```

## 📚 Next Steps

1. Add your data to `data/raw/`
2. Explore with Jupyter notebooks
3. Build your model in `src/models/`
4. Evaluate and visualize results
5. Deploy with Streamlit or FastAPI

---

**Happy Coding! 🚀**
