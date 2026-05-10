"""
Split large files into smaller parts for Terabox upload.
Terabox free users may encounter issues with files > 4GB.
This script splits files into ~1.9GB parts using 7z.

Usage:
    python archive_split.py --source "models/llm" --output "backup" --size 1900
    python archive_split.py --source "data/kuera_database.db" --output "backup" --size 1900
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def check_7z() -> bool:
    """Check if 7z is installed."""
    try:
        result = subprocess.run(["7z"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0 or "7-Zip" in result.stdout
    except FileNotFoundError:
        return False


def archive_folder(source: Path, output_dir: Path, size_mb: int, name: str) -> bool:
    """Archive a folder into split parts using 7z."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{name}.7z"

    size_param = f"{size_mb}m"  # e.g., "1900m"

    cmd = [
        "7z", "a",
        f"-v{size_param}",  # Split into volumes
        "-mx=0",            # Store (no compression, faster)
        str(output_file),
        str(source),
    ]

    print(f"[ARCHIVE] {source} -> {output_dir}/{name}.7z.*")
    print(f"[ARCHIVE] Volume size: ~{size_mb} MB each")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if result.returncode == 0:
            # List created files
            parts = sorted(output_dir.glob(f"{name}.7z.*"))
            print(f"[OK] Created {len(parts)} part(s):")
            for part in parts:
                size = part.stat().st_size / (1024**2)
                print(f"  - {part.name} ({size:.2f} MB)")
            return True
        else:
            print(f"[ERROR] 7z failed:\n{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("[ERROR] Archive creation timed out (after 1 hour)")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def archive_single_file(source: Path, output_dir: Path, size_mb: int, name: str) -> bool:
    """Archive a single file into split parts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{name}.7z"

    size_param = f"{size_mb}m"

    cmd = [
        "7z", "a",
        f"-v{size_param}",
        "-mx=0",
        str(output_file),
        str(source),
    ]

    print(f"[ARCHIVE] {source} ({source.stat().st_size / (1024**3):.2f} GB)")
    print(f"[ARCHIVE] -> {output_dir}/{name}.7z.* (~{size_mb} MB each)")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if result.returncode == 0:
            parts = sorted(output_dir.glob(f"{name}.7z.*"))
            print(f"[OK] Created {len(parts)} part(s):")
            for part in parts:
                size = part.stat().st_size / (1024**2)
                print(f"  - {part.name} ({size:.2f} MB)")
            return True
        else:
            print(f"[ERROR] 7z failed:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Split files into smaller archives")
    parser.add_argument("--source", "-s", required=True, help="Source file or folder")
    parser.add_argument("--output", "-o", default="backup", help="Output directory")
    parser.add_argument("--size", type=int, default=1900, help="Volume size in MB (default: 1900)")
    parser.add_argument("--name", "-n", help="Archive base name (default: source name)")

    args = parser.parse_args()

    if not check_7z():
        print("[ERROR] 7z not found. Please install 7-Zip first.")
        print("[INFO] Download: https://www.7-zip.org/download.html")
        print("[INFO] Make sure 7z.exe is in your PATH")
        sys.exit(1)

    source = Path(args.source).resolve()
    if not source.exists():
        print(f"[ERROR] Source not found: {source}")
        sys.exit(1)

    output_dir = Path(args.output).resolve()
    name = args.name or source.name.replace(".", "_")

    timestamp = datetime.now().strftime("%Y%m%d")
    name = f"{name}_{timestamp}"

    if source.is_dir():
        success = archive_folder(source, output_dir, args.size, name)
    else:
        success = archive_single_file(source, output_dir, args.size, name)

    if success:
        print(f"\n[OK] Archive complete. Upload these parts to Terabox:")
        print(f"  cd scripts/terabox")
        print(f"  python upload.py --folder \"{output_dir}\" --remote \"/KUERA_Backup/{name}\"")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
