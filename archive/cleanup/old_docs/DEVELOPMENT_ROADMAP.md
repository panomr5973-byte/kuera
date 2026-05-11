# 🗺️ Development Roadmap - AI Project

Panduan lengkap untuk mengembangkan project AI dari yang sudah ada menjadi production-ready.

---

## 📍 STATUS SAAT INI

✅ **SUDAH ADA:**
- Virtual environment dengan 20+ library AI/ML
- Data processing pipeline (automated)
- Multi-model training (6 algorithms)
- Streamlit dashboard (5 pages)
- Sample dataset & trained model

---

## 🎯 PHASE 1: MENGGUNAKAN DATA SENDIRI (Prioritas Tinggi)

### Langkah 1.1: Persiapkan Data Anda
```bash
# 1. Copy data ke folder
Copy-Item "C:\path\to\your\data.csv" "data\raw\my_data.csv"

# 2. Update pipeline config
# Edit: src/data/pipeline.py
```

### Langkah 1.2: Update Pipeline Configuration
```python
# Di src/data/pipeline.py, ubah bagian ini:

pipeline = DataPipeline()
pipeline.config['target_column'] = 'nama_kolom_target_anda'  # GANTI!
pipeline.config['categorical_columns'] = ['kolom1', 'kolom2']  # GANTI!
pipeline.config['drop_columns'] = ['id', 'timestamp']  # GANTI!
pipeline.config['handle_missing'] = 'fill_mean'  # atau 'drop', 'fill_median'

X_train, X_test, y_train, y_test = pipeline.run(
    'data/raw/my_data.csv',  # GANTI!
    'data/processed/'
)
```

### Langkah 1.3: Jalankan Pipeline
```bash
python src/data/pipeline.py
```

---

## 🎯 PHASE 2: IMPROVE MODEL PERFORMANCE

### 2.1 Feature Engineering Lebih Baik
Tambahkan di `src/data/pipeline.py`:

```python
def feature_engineering(self, df):
    """Advanced feature engineering"""
    
    # 1. Polynomial features
    from sklearn.preprocessing import PolynomialFeatures
    poly = PolynomialFeatures(degree=2, include_bias=False)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    poly_features = poly.fit_transform(df[numeric_cols])
    
    # 2. Interaction features
    df['feature_A_x_B'] = df['feature_A'] * df['feature_B']
    
    # 3. Binning untuk numerical
    df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 50, 100], labels=['young', 'adult', 'middle', 'senior'])
    
    # 4. Log transformation untuk skewed data
    df['income_log'] = np.log1p(df['income'])
    
    return df
```

### 2.2 Hyperparameter Tuning
Update `src/models/train_example.py`:

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

def tune_hyperparameters(self, X_train, y_train):
    """Tune hyperparameters untuk best model"""
    
    param_grid = {
        'xgboost': {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 5, 7, 10],
            'learning_rate': [0.01, 0.1, 0.3],
            'subsample': [0.8, 0.9, 1.0]
        }
    }
    
    model = XGBClassifier(random_state=42)
    grid_search = GridSearchCV(
        model, 
        param_grid['xgboost'],
        cv=5,
        scoring='f1_weighted',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    print(f"Best params: {grid_search.best_params_}")
    print(f"Best score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_
```

### 2.3 Cross-Validation
```python
from sklearn.model_selection import cross_val_score, StratifiedKFold

def cross_validate_model(self, model, X, y, cv=5):
    """Cross validation yang lebih robust"""
    cv_strategy = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    
    scores = cross_val_score(model, X, y, cv=cv_strategy, scoring='f1_weighted')
    
    print(f"CV Scores: {scores}")
    print(f"Mean: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
    
    return scores
```

---

## 🎯 PHASE 3: PRODUCTION DEPLOYMENT

### 3.1 Create Production API
Buat file baru: `app/production_api.py`

```python
"""
Production API dengan model loading dan error handling
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Production ML API", version="2.0.0")

# Load model saat startup
model = None
model_metadata = None

def load_model():
    """Load model terbaik"""
    global model, model_metadata
    try:
        with open('models/best_model_logistic_regression.pkl', 'rb') as f:
            model = pickle.load(f)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {e}")

@app.on_event("startup")
async def startup_event():
    load_model()

class PredictionRequest(BaseModel):
    features: List[float]
    request_id: Optional[str] = None

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    model_version: str
    timestamp: str
    request_id: Optional[str] = None

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Endpoint untuk prediction"""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Prediction
        features = np.array(request.features).reshape(1, -1)
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0].max()
        
        # Logging
        logger.info(f"Prediction made: {prediction} (confidence: {probability:.4f})")
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=float(probability),
            model_version="1.0.0",
            timestamp=datetime.now().isoformat(),
            request_id=request.request_id
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/model/info")
async def model_info():
    """Model information"""
    return {
        "model_type": "LogisticRegression",
        "version": "1.0.0",
        "features": 9,
        "last_trained": "2024-01-01T00:00:00"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Jalankan:
```bash
python app/production_api.py
```

### 3.2 Docker Deployment
Buat `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["python", "app/production_api.py"]
```

Build dan run:
```bash
docker build -t ai-project .
docker run -p 8000:8000 ai-project
```

---

## 🎯 PHASE 4: MONITORING & MAINTENANCE

### 4.1 Model Monitoring
Buat `src/monitoring/model_monitor.py`:

```python
"""
Model Monitoring dengan Evidently
"""

import pandas as pd
import numpy as np
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset
import json
from datetime import datetime

class ModelMonitor:
    """Monitor model performance dan data drift"""
    
    def __init__(self, reference_data_path):
        self.reference_data = pd.read_csv(reference_data_path)
        self.metrics_history = []
    
    def check_data_drift(self, current_data, save_path=None):
        """Check apakah data ada drift"""
        
        drift_report = Report(metrics=[DataDriftPreset()])
        drift_report.run(
            reference_data=self.reference_data,
            current_data=current_data
        )
        
        # Save report
        if save_path:
            drift_report.save_html(save_path)
        
        # Check if drift detected
        results = drift_report.as_dict()
        drift_detected = results['metrics'][0]['result']['dataset_drift']
        
        return drift_detected, results
    
    def log_prediction(self, features, prediction, probability, timestamp=None):
        """Log setiap prediction untuk monitoring"""
        
        log_entry = {
            'timestamp': timestamp or datetime.now().isoformat(),
            'features': features,
            'prediction': prediction,
            'probability': probability
        }
        
        self.metrics_history.append(log_entry)
        
        # Save periodically
        if len(self.metrics_history) % 100 == 0:
            self._save_logs()
    
    def _save_logs(self):
        """Save logs ke file"""
        df = pd.DataFrame(self.metrics_history)
        df.to_csv('logs/predictions_log.csv', mode='a', header=False, index=False)
        self.metrics_history = []
    
    def generate_monitoring_dashboard(self):
        """Generate monitoring dashboard"""
        
        # Calculate metrics
        df = pd.DataFrame(self.metrics_history)
        
        metrics = {
            'total_predictions': len(df),
            'avg_confidence': df['probability'].mean() if len(df) > 0 else 0,
            'prediction_distribution': df['prediction'].value_counts().to_dict() if len(df) > 0 else {},
            'last_updated': datetime.now().isoformat()
        }
        
        with open('logs/monitoring_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        return metrics

# Usage
if __name__ == "__main__":
    monitor = ModelMonitor('data/processed/X_train.csv')
    
    # Simulate current data
    current = pd.read_csv('data/processed/X_test.csv')
    
    drift_detected, results = monitor.check_data_drift(current, 'reports/drift_report.html')
    print(f"Drift detected: {drift_detected}")
```

### 4.2 Automated Retraining
Buat `src/monitoring/auto_retrain.py`:

```python
"""
Auto-retraining ketika performance turun
"""

import schedule
import time
from datetime import datetime
import pandas as pd
from sklearn.metrics import f1_score
import pickle

class AutoRetrainer:
    """Auto retrain model ketika metrics turun"""
    
    def __init__(self, threshold=0.05):
        self.threshold = threshold  # Retrain kalau drop > 5%
        self.baseline_score = None
        self.model_path = 'models/best_model_logistic_regression.pkl'
    
    def check_performance(self, X_test, y_test):
        """Check current model performance"""
        
        with open(self.model_path, 'rb') as f:
            model = pickle.load(f)
        
        y_pred = model.predict(X_test)
        current_score = f1_score(y_test, y_pred, average='weighted')
        
        if self.baseline_score is None:
            self.baseline_score = current_score
            return True, current_score
        
        drop = self.baseline_score - current_score
        
        if drop > self.threshold:
            print(f"⚠️ Performance dropped by {drop:.4f}. Retraining needed!")
            return False, current_score
        
        return True, current_score
    
    def retrain_model(self):
        """Trigger retraining"""
        print("🔄 Starting retraining...")
        
        # Import training script
        from src.models.train_example import ModelTrainer
        
        X_train = pd.read_csv('data/processed/X_train.csv')
        X_test = pd.read_csv('data/processed/X_test.csv')
        y_train = pd.read_csv('data/processed/y_train.csv').values.ravel()
        y_test = pd.read_csv('data/processed/y_test.csv').values.ravel()
        
        trainer = ModelTrainer(experiment_name="auto_retrain")
        trainer.train_all(X_train, X_test, y_train, y_test)
        trainer.save_best_model()
        
        # Update baseline
        _, new_score = self.check_performance(X_test, y_test)
        self.baseline_score = new_score
        
        print(f"✅ Retraining completed. New score: {new_score:.4f}")
    
    def run_daily_check(self):
        """Run check setiap hari"""
        X_test = pd.read_csv('data/processed/X_test.csv')
        y_test = pd.read_csv('data/processed/y_test.csv').values.ravel()
        
        is_good, score = self.check_performance(X_test, y_test)
        
        if not is_good:
            self.retrain_model()
        else:
            print(f"✅ Model healthy. Score: {score:.4f}")

# Schedule
def start_monitoring():
    retrainer = AutoRetrainer(threshold=0.05)
    
    # Check setiap hari jam 3 pagi
    schedule.every().day.at("03:00").do(retrainer.run_daily_check)
    
    print("🤖 Auto-retraining scheduler started...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    start_monitoring()
```

---

## 🎯 PHASE 5: ADVANCED FEATURES

### 5.1 Explainable AI (XAI)
```python
import shap

# SHAP explanations
def explain_prediction(model, X_sample):
    explainer = shap.TreeExplainer(model) if hasattr(model, 'tree_') else shap.KernelExplainer(model.predict, X_sample)
    shap_values = explainer.shap_values(X_sample)
    
    # Save plot
    shap.summary_plot(shap_values, X_sample, show=False)
    plt.savefig('reports/shap_summary.png')
    
    return shap_values
```

### 5.2 A/B Testing
```python
class ABTesting:
    """A/B testing untuk model comparison"""
    
    def __init__(self, model_a, model_b, traffic_split=0.5):
        self.model_a = model_a
        self.model_b = model_b
        self.traffic_split = traffic_split
        self.results = {'A': [], 'B': []}
    
    def route_request(self, features):
        """Route ke model A atau B berdasarkan split"""
        import random
        
        if random.random() < self.traffic_split:
            return 'A', self.model_a.predict(features)
        else:
            return 'B', self.model_b.predict(features)
    
    def analyze_results(self):
        """Analyze which model better"""
        # Statistical test
        from scipy import stats
        
        t_stat, p_value = stats.ttest_ind(
            self.results['A'], 
            self.results['B']
        )
        
        return {
            'model_a_mean': np.mean(self.results['A']),
            'model_b_mean': np.mean(self.results['B']),
            'p_value': p_value,
            'winner': 'A' if np.mean(self.results['A']) > np.mean(self.results['B']) else 'B'
        }
```

### 5.3 Batch Prediction
```python
@app.post("/predict/batch")
async def predict_batch(file: UploadFile = File(...)):
    """Batch prediction via file upload"""
    
    df = pd.read_csv(file.file)
    predictions = model.predict(df)
    probabilities = model.predict_proba(df).max(axis=1)
    
    result_df = pd.DataFrame({
        'prediction': predictions,
        'confidence': probabilities
    })
    
    # Save to buffer
    output = io.StringIO()
    result_df.to_csv(output, index=False)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=predictions.csv"}
    )
```

---

## 🎯 PHASE 6: INTEGRATION

### 6.1 Database Integration
```python
from sqlalchemy import create_engine
import pandas as pd

# Connect ke database
engine = create_engine('postgresql://user:pass@localhost/dbname')

# Read data
df = pd.read_sql("SELECT * FROM customers", engine)

# Save predictions
df.to_sql('predictions', engine, if_exists='append', index=False)
```

### 6.2 Cloud Deployment
**AWS:**
```bash
# Deploy ke AWS Elastic Beanstalk
eb init -p python-3.10 my-ai-app
eb create my-ai-env
eb open
```

**Google Cloud:**
```bash
# Deploy ke Cloud Run
gcloud builds submit --tag gcr.io/my-project/ai-app
gcloud run deploy --image gcr.io/my-project/ai-app --platform managed
```

---

## 📋 CHECKLIST IMPLEMENTASI

### Week 1: Foundation
- [ ] Ganti dengan data sendiri
- [ ] Training model dengan data real
- [ ] Test API endpoints

### Week 2: Improvement
- [ ] Feature engineering lebih baik
- [ ] Hyperparameter tuning
- [ ] Cross-validation

### Week 3: Production
- [ ] Production API dengan error handling
- [ ] Docker container
- [ ] Deployment ke cloud

### Week 4: Monitoring
- [ ] Setup monitoring dashboard
- [ ] Auto-retraining
- [ ] Alert system

---

## 🚀 NEXT ACTIONS (Prioritas)

**1. Segera Lakukan:**
```bash
# 1. Siapkan data Anda
copy data ke data/raw/

# 2. Update config di pipeline.py
# Edit: target_column, categorical_columns, dll

# 3. Jalankan ulang
python run_pipeline.py --step all
```

**2. Pilih Satu Fokus:**
- **Fokus A**: Model Accuracy → Lakukan Phase 2 (hyperparameter tuning)
- **Fokus B**: Production Deployment → Lakukan Phase 3 (API + Docker)
- **Fokus C**: Monitoring → Lakukan Phase 4 (Evidently + auto-retrain)

**3. Minta Bantuan:**
Katakan saya fokus mana yang mau dikerjakan, saya akan bantu implementasi detailnya!

---

**Pertanyaan untuk Anda:**
1. Apakah Anda sudah punya dataset sendiri?
2. Apa tujuan utama: accuracy, deployment, atau monitoring?
3. Deadline kapan project ini harus jadi?
