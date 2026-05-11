#!/usr/bin/env python
"""
Download LLM Models for Kuwera
Script untuk mendownload model AI dari HuggingFace
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


def print_header(title):
    print("="*70)
    print(title.center(70))
    print("="*70)


def load_registry():
    """Load model registry"""
    registry_path = Path("models/llm/llm_registry.json")
    if registry_path.exists():
        with open(registry_path) as f:
            return json.load(f)
    return None


def check_huggingface_cli():
    """Check if huggingface-cli is available"""
    try:
        result = subprocess.run(
            ["huggingface-cli", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_huggingface_cli():
    """Install huggingface-cli"""
    print("\n[INSTALL] Installing huggingface-cli...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "huggingface-hub[cli]",
            "-q"
        ])
        print("[OK] huggingface-cli installed successfully")
        return True
    except Exception as e:
        print(f"[FAILED] Could not install huggingface-cli: {e}")
        return False


def download_model(model_info, models_dir):
    """Download a single model"""
    repo = model_info['repo']
    filename = model_info['filename']
    name = model_info['name']
    size_gb = model_info['size_gb']
    
    output_path = models_dir / filename
    
    # Check if already exists
    if output_path.exists():
        actual_size = output_path.stat().st_size / (1024**3)
        print(f"  [SKIP] {name} already exists ({actual_size:.2f} GB)")
        return True
    
    print(f"\n  [DOWNLOAD] {name}")
    print(f"    Repository: {repo}")
    print(f"    File: {filename}")
    print(f"    Expected size: ~{size_gb} GB")
    print(f"    This may take a few minutes...")
    print()
    
    try:
        # Use huggingface-cli to download
        subprocess.check_call([
            "huggingface-cli", "download",
            repo,
            filename,
            "--local-dir", str(models_dir),
            "--local-dir-use-symlinks", "False"
        ])
        
        # Verify download
        if output_path.exists():
            actual_size = output_path.stat().st_size / (1024**3)
            print(f"  [OK] Downloaded: {name} ({actual_size:.2f} GB)")
            return True
        else:
            print(f"  [FAILED] File not found after download: {filename}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"  [FAILED] {name}: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n  [CANCELLED] Download interrupted by user")
        return False


def download_recommended():
    """Download recommended models (top 5)"""
    print_header("DOWNLOADING RECOMMENDED MODELS")
    
    registry = load_registry()
    if not registry:
        print("[ERROR] Model registry not found. Run create_model_registry.py first.")
        return
    
    # Check huggingface-cli
    if not check_huggingface_cli():
        if not install_huggingface_cli():
            print("[ERROR] Cannot proceed without huggingface-cli")
            return
    
    models_dir = Path("models/llm")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Get top 5 recommended models
    models = sorted(registry['available_models'], key=lambda x: x['priority'])[:5]
    
    print(f"\nWill download {len(models)} recommended models:")
    total_size = sum(m['size_gb'] for m in models)
    print(f"Total estimated size: {total_size:.1f} GB")
    print(f"Download location: {models_dir.absolute()}")
    print()
    
    success = []
    failed = []
    
    for i, model in enumerate(models, 1):
        print(f"[{i}/{len(models)}] Processing {model['name']}...")
        if download_model(model, models_dir):
            success.append(model)
        else:
            failed.append(model)
    
    # Update registry
    registry['downloaded'] = success
    registry['failed'] = failed
    with open(models_dir / 'llm_registry.json', 'w') as f:
        json.dump(registry, f, indent=2)
    
    # Summary
    print_header("DOWNLOAD SUMMARY")
    print(f"\nSuccessful: {len(success)}/{len(models)}")
    if success:
        print("\nDownloaded models:")
        for m in success:
            print(f"  [OK] {m['name']} ({m['size_gb']} GB)")
    
    if failed:
        print(f"\nFailed: {len(failed)}")
        for m in failed:
            print(f"  [X] {m['name']}")
    
    print()
    print(f"Models saved to: {models_dir.absolute()}")
    print("="*70)


def download_all():
    """Download all models"""
    print_header("DOWNLOADING ALL MODELS")
    
    registry = load_registry()
    if not registry:
        print("[ERROR] Model registry not found.")
        return
    
    if not check_huggingface_cli():
        if not install_huggingface_cli():
            print("[ERROR] Cannot proceed without huggingface-cli")
            return
    
    models_dir = Path("models/llm")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    models = registry['available_models']
    total_size = sum(m['size_gb'] for m in models)
    
    print(f"\nWill download ALL {len(models)} models")
    print(f"Total estimated size: {total_size:.1f} GB")
    print("This will take a significant amount of time and disk space!")
    print()
    
    confirm = input("Continue? (yes/no): ").lower()
    if confirm != 'yes':
        print("Download cancelled.")
        return
    
    success = []
    failed = []
    
    for i, model in enumerate(models, 1):
        print(f"\n[{i}/{len(models)}] Processing {model['name']}...")
        if download_model(model, models_dir):
            success.append(model)
        else:
            failed.append(model)
    
    # Update registry
    registry['downloaded'] = success
    registry['failed'] = failed
    with open(models_dir / 'llm_registry.json', 'w') as f:
        json.dump(registry, f, indent=2)
    
    print_header("DOWNLOAD SUMMARY")
    print(f"Successful: {len(success)}/{len(models)}")
    print(f"Failed: {len(failed)}")


def show_status():
    """Show download status"""
    print_header("MODEL DOWNLOAD STATUS")
    
    registry = load_registry()
    if not registry:
        print("[ERROR] Model registry not found.")
        return
    
    models_dir = Path("models/llm")
    
    print("\n[AVAILABLE MODELS]")
    for m in registry['available_models']:
        status = "Not downloaded"
        if any(d['name'] == m['name'] for d in registry.get('downloaded', [])):
            status = "Downloaded"
        elif any(d['name'] == m['name'] for d in registry.get('failed', [])):
            status = "Failed"
        
        # Check if file actually exists
        file_path = models_dir / m['filename']
        if file_path.exists():
            actual_size = file_path.stat().st_size / (1024**3)
            status = f"Downloaded ({actual_size:.2f} GB)"
        
        print(f"  {m['name']:35} | {m['size_gb']:.1f} GB | {status}")
    
    # Calculate total downloaded size
    total_downloaded = 0
    for m in registry['available_models']:
        file_path = models_dir / m['filename']
        if file_path.exists():
            total_downloaded += file_path.stat().st_size / (1024**3)
    
    print()
    print(f"Total downloaded: {total_downloaded:.1f} GB")
    print("="*70)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_header("KUWERA MODEL DOWNLOADER")
        print("\nUsage:")
        print("  python download_models.py recommended  # Download top 5 models")
        print("  python download_models.py all          # Download all models")
        print("  python download_models.py status       # Show download status")
        print()
        print("Recommended models are pre-selected for Bahasa Indonesia support")
        print("and optimal size/performance ratio.")
        print("="*70)
        return
    
    command = sys.argv[1].lower()
    
    if command == "recommended":
        download_recommended()
    elif command == "all":
        download_all()
    elif command == "status":
        show_status()
    else:
        print(f"Unknown command: {command}")
        print("Use: recommended, all, or status")


if __name__ == "__main__":
    main()
