#!/usr/bin/env python3
"""
Script untuk copy file AI Audit Toolkit ke WSL
"""

import shutil
import os
from pathlib import Path


def copy_to_wsl():
    """Copy file ke WSL"""
    
    # List file yang akan di-copy
    files = [
        'audit_toolkit_complete.py',
        'template_audit_spi.py',
        'template_audit_kinerja.py',
        'template_master.py',
        'README_AUDIT_AI.md'
    ]
    
    # Source folder (Windows)
    source_dir = Path('C:/AI-Project')
    
    # Target folder (WSL) - via /mnt/c
    target_dir = Path('//wsl$/Ubuntu/home/audit-user/ai-audit')
    
    # Alternatif: gunakan /mnt/c path
    wsl_target = '/mnt/c/AI-Project/wsl_export'
    
    print("="*60)
    print("COPY AI AUDIT TOOLKIT KE WSL")
    print("="*60)
    print()
    
    # Cek apakah WSL tersedia
    if not target_dir.exists():
        print("⚠️  WSL path tidak langsung terdeteksi.")
        print("   Menggunakan alternatif...")
        
        # Buat folder export di Windows
        export_dir = Path('C:/AI-Project/wsl_export')
        export_dir.mkdir(exist_ok=True)
        
        print(f"📁 Folder export: {export_dir}")
        print()
        
        # Copy ke folder export
        for file in files:
            source = source_dir / file
            target = export_dir / file
            
            if source.exists():
                shutil.copy2(source, target)
                print(f"✅ {file}")
            else:
                print(f"❌ {file} - tidak ditemukan")
        
        print()
        print("="*60)
        print("CARA COPY KE WSL MANUAL:")
        print("="*60)
        print()
        print("Opsi 1 - Via Windows Explorer:")
        print("   1. Buka Explorer")
        print("   2. Ketik di address bar: \\\\wsl$\\Ubuntu\\home\\audit-user")
        print("   3. Copy file dari C:\\AI-Project\\wsl_export ke folder tersebut")
        print()
        print("Opsi 2 - Via WSL Terminal:")
        print("   1. Buka WSL")
        print("   2. Jalankan command:")
        print("      mkdir -p ~/ai-audit")
        print("      cp /mnt/c/AI-Project/wsl_export/*.py ~/ai-audit/")
        print("      cp /mnt/c/AI-Project/wsl_export/*.md ~/ai-audit/")
        print()
        print("Opsi 3 - Copy langsung (jika WSL running):")
        print("   Buka Command Prompt/PowerShell, jalankan:")
        print("   wsl cp /mnt/c/AI-Project/wsl_export/*.py ~/ai-audit/")
        print()
        
    else:
        # WSL terdeteksi, copy langsung
        target_dir.mkdir(exist_ok=True)
        
        for file in files:
            source = source_dir / file
            target = target_dir / file
            
            if source.exists():
                shutil.copy2(source, target)
                print(f"✅ {file}")
            else:
                print(f"❌ {file} - tidak ditemukan")
        
        print()
        print("✅ Copy selesai!")
        print(f"📁 File tersedia di: {target_dir}")


def create_zip():
    """Buat ZIP file untuk kemudahan transfer"""
    import zipfile
    
    files = [
        'audit_toolkit_complete.py',
        'template_audit_spi.py',
        'template_audit_kinerja.py',
        'template_master.py',
        'README_AUDIT_AI.md'
    ]
    
    zip_path = Path('C:/AI-Project/AI_Audit_Toolkit.zip')
    
    print("📦 Membuat ZIP file...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            file_path = Path(f'C:/AI-Project/{file}')
            if file_path.exists():
                zipf.write(file_path, file)
                print(f"   Added: {file}")
    
    print(f"\n✅ ZIP tersimpan: {zip_path}")
    print("\nCara pakai:")
    print("   1. Copy ZIP ke WSL: cp /mnt/c/AI-Project/AI_Audit_Toolkit.zip ~/")
    print("   2. Extract: unzip ~/AI_Audit_Toolkit.zip -d ~/ai-audit/")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'zip':
        create_zip()
    else:
        copy_to_wsl()
        print()
        print("-"*60)
        print("Untuk membuat ZIP file, jalankan:")
        print("   python copy_to_wsl.py zip")
        print("-"*60)
