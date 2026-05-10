"""
Data Processing Pipeline
========================
Pipeline lengkap untuk data processing dari raw hingga ready for modeling.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataPipeline:
    """
    Pipeline untuk data processing end-to-end.
    
    Usage:
        pipeline = DataPipeline(config_path='config/pipeline_config.json')
        pipeline.run('data/raw/dataset.csv', 'data/processed/')
    """
    
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.metadata = {
            'created_at': datetime.now().isoformat(),
            'steps': []
        }
        
    def _load_config(self, config_path):
        """Load configuration file"""
        default_config = {
            'test_size': 0.2,
            'random_state': 42,
            'target_column': 'target',
            'drop_columns': [],
            'categorical_columns': [],
            'numerical_columns': [],
            'handle_missing': 'drop',  # 'drop', 'fill_mean', 'fill_median'
            'scaling': True
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                default_config.update(config)
        
        return default_config
    
    def load_data(self, file_path):
        """Load data dari berbagai format"""
        logger.info(f"Loading data from {file_path}")
        
        path = Path(file_path)
        
        if path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif path.suffix == '.parquet':
            df = pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
        self.metadata['original_shape'] = df.shape
        return df
    
    def handle_missing_values(self, df):
        """Handle missing values sesuai config"""
        logger.info("Handling missing values")
        
        missing_before = df.isnull().sum().sum()
        
        if self.config['handle_missing'] == 'drop':
            df = df.dropna()
        elif self.config['handle_missing'] == 'fill_mean':
            df = df.fillna(df.mean(numeric_only=True))
        elif self.config['handle_missing'] == 'fill_median':
            df = df.fillna(df.median(numeric_only=True))
        
        missing_after = df.isnull().sum().sum()
        logger.info(f"Missing values: {missing_before} -> {missing_after}")
        
        self.metadata['steps'].append({
            'step': 'handle_missing',
            'method': self.config['handle_missing'],
            'dropped_rows': missing_before - missing_after
        })
        
        return df
    
    def feature_engineering(self, df):
        """Tambahan fitur baru (customizable)"""
        logger.info("Feature engineering")
        
        # Contoh: Tambah fitur datetime jika ada kolom date
        date_columns = df.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            df[f'{col}_year'] = df[col].dt.year
            df[f'{col}_month'] = df[col].dt.month
            df[f'{col}_day'] = df[col].dt.day
        
        # Contoh: Statistical features untuk numerical
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(num_cols) > 1:
            df['num_sum'] = df[num_cols].sum(axis=1)
            df['num_mean'] = df[num_cols].mean(axis=1)
        
        self.metadata['steps'].append({'step': 'feature_engineering'})
        return df
    
    def encode_categorical(self, df):
        """Encode categorical variables"""
        logger.info("Encoding categorical variables")
        
        cat_cols = self.config['categorical_columns'] or df.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()
        
        # Exclude target column
        if self.config['target_column'] in cat_cols:
            cat_cols.remove(self.config['target_column'])
        
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le
            logger.info(f"Encoded {col}: {len(le.classes_)} categories")
        
        self.metadata['steps'].append({
            'step': 'encode_categorical',
            'columns': cat_cols
        })
        
        return df
    
    def scale_features(self, df):
        """Scale numerical features"""
        if not self.config['scaling']:
            return df
        
        logger.info("Scaling numerical features")
        
        num_cols = self.config['numerical_columns'] or df.select_dtypes(
            include=[np.number]
        ).columns.tolist()
        
        # Exclude target
        if self.config['target_column'] in num_cols:
            num_cols.remove(self.config['target_column'])
        
        if num_cols:
            df[num_cols] = self.scaler.fit_transform(df[num_cols])
            logger.info(f"Scaled {len(num_cols)} numerical columns")
        
        self.metadata['steps'].append({'step': 'scaling', 'columns': num_cols})
        return df
    
    def split_data(self, df):
        """Split data menjadi train dan test"""
        logger.info("Splitting data")
        
        target = self.config['target_column']
        X = df.drop(columns=[target])
        y = df[target]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.config['test_size'],
            random_state=self.config['random_state'],
            stratify=y if y.dtype == 'object' or y.nunique() < 10 else None
        )
        
        logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
        
        self.metadata['split'] = {
            'train_size': len(X_train),
            'test_size': len(X_test),
            'test_ratio': self.config['test_size']
        }
        
        return X_train, X_test, y_train, y_test
    
    def save_processed_data(self, output_dir, X_train, X_test, y_train, y_test):
        """Save processed data"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save as CSV
        X_train.to_csv(output_path / 'X_train.csv', index=False)
        X_test.to_csv(output_path / 'X_test.csv', index=False)
        y_train.to_csv(output_path / 'y_train.csv', index=False)
        y_test.to_csv(output_path / 'y_test.csv', index=False)
        
        # Save metadata
        with open(output_path / 'pipeline_metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
        
        logger.info(f"Saved processed data to {output_path}")
    
    def run(self, input_path, output_dir):
        """Run complete pipeline"""
        logger.info("="*50)
        logger.info("STARTING DATA PIPELINE")
        logger.info("="*50)
        
        # 1. Load
        df = self.load_data(input_path)
        
        # 2. Drop specified columns
        if self.config['drop_columns']:
            df = df.drop(columns=self.config['drop_columns'], errors='ignore')
        
        # 3. Handle missing
        df = self.handle_missing_values(df)
        
        # 4. Feature engineering
        df = self.feature_engineering(df)
        
        # 5. Encode categorical
        df = self.encode_categorical(df)
        
        # 6. Scale
        df = self.scale_features(df)
        
        # 7. Split
        X_train, X_test, y_train, y_test = self.split_data(df)
        
        # 8. Save
        self.save_processed_data(output_dir, X_train, X_test, y_train, y_test)
        
        logger.info("="*50)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*50)
        
        return X_train, X_test, y_train, y_test


def create_sample_data(output_path='data/raw/sample_dataset.csv', n_samples=1000):
    """Create sample dataset untuk demo"""
    logger.info(f"Creating sample dataset with {n_samples} samples")
    
    np.random.seed(42)
    
    data = {
        'customer_id': range(1, n_samples + 1),
        'age': np.random.randint(18, 80, n_samples),
        'income': np.random.normal(50000, 15000, n_samples).astype(int),
        'gender': np.random.choice(['Male', 'Female'], n_samples),
        'city': np.random.choice(['Jakarta', 'Surabaya', 'Bandung', 'Medan'], n_samples),
        'purchase_amount': np.random.exponential(1000, n_samples),
        'num_purchases': np.random.poisson(5, n_samples),
        'is_member': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
        'target': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])  # Churn prediction
    }
    
    # Add some missing values
    df = pd.DataFrame(data)
    mask = np.random.random(df.shape) < 0.05
    df = df.mask(mask)
    
    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Sample dataset saved to {output_path}")
    
    return df


if __name__ == "__main__":
    # Create sample data
    create_sample_data()
    
    # Run pipeline
    pipeline = DataPipeline()
    pipeline.config['target_column'] = 'target'
    pipeline.config['categorical_columns'] = ['gender', 'city']
    pipeline.config['drop_columns'] = ['customer_id']
    
    X_train, X_test, y_train, y_test = pipeline.run(
        'data/raw/sample_dataset.csv',
        'data/processed/'
    )
    
    print("\n[OK] Pipeline completed!")
    print(f"Train set: {X_train.shape}")
    print(f"Test set: {X_test.shape}")
