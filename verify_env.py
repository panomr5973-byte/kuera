#!/usr/bin/env python3
"""
Verifikasi Environment AI Project
==================================
Script untuk memverifikasi semua library yang diperlukan sudah terinstall.
"""

import sys

def check_library(name, import_name=None):
    """Check if a library is installed"""
    if import_name is None:
        import_name = name
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {name:20s} - {version}")
        return True
    except ImportError:
        print(f"❌ {name:20s} - NOT INSTALLED")
        return False

def main():
    print("=" * 60)
    print("AI PROJECT ENVIRONMENT VERIFICATION")
    print("=" * 60)
    
    libraries = [
        ("Pandas", "pandas"),
        ("NumPy", "numpy"),
        ("Matplotlib", "matplotlib"),
        ("Seaborn", "seaborn"),
        ("Scikit-learn", "sklearn"),
        ("PyTorch", "torch"),
        ("XGBoost", "xgboost"),
        ("LightGBM", "lightgbm"),
        ("MLflow", "mlflow"),
        ("FastAPI", "fastapi"),
        ("Streamlit", "streamlit"),
        ("ONNX", "onnx"),
        ("Transformers", "transformers"),
        ("Datasets", "datasets"),
        ("Accelerate", "accelerate"),
        ("SHAP", "shap"),
        ("Evidently", "evidently"),
        ("Jupyter", "jupyter"),
        ("OpenAI", "openai"),
    ]
    
    # Optional libraries
    optional = [
        ("Polars", "polars"),
        ("DuckDB", "duckdb"),
        ("PyArrow", "pyarrow"),
    ]
    
    print("\n📦 Core Libraries:")
    print("-" * 40)
    all_ok = True
    for name, import_name in libraries:
        if not check_library(name, import_name):
            all_ok = False
    
    print("\n📦 Optional Libraries:")
    print("-" * 40)
    for name, import_name in optional:
        check_library(name, import_name)
    
    print("\n" + "=" * 60)
    
    # Check PyTorch CUDA
    try:
        import torch
        if torch.cuda.is_available():
            print(f"🚀 PyTorch CUDA: Available (GPU: {torch.cuda.get_device_name(0)})")
        else:
            print("⚠️  PyTorch CUDA: Not available (CPU only)")
    except:
        pass
    
    # Check Python version
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    if all_ok:
        print("\n✨ All core libraries are installed!")
    else:
        print("\n⚠️  Some libraries are missing. Install with: pip install <library>")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
