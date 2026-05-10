"""
Data Preprocessing Script
=========================
Contoh script untuk preprocessing data.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_data(file_path: str) -> pd.DataFrame:
    """Load data dari CSV"""
    return pd.read_csv(file_path)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Basic data cleaning"""
    # Drop duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df = df.dropna()
    
    return df

def save_processed_data(df: pd.DataFrame, output_path: str):
    """Save processed data"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Saved processed data to {output_path}")

if __name__ == "__main__":
    # Example usage
    print("Data preprocessing module ready!")
