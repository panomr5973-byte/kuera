#!/usr/bin/env python3
"""KUERA Workspace Sanitizer — Phase 8 Cleanup

Handles:
- Archive redundant fix/download/chat/test/demo scripts
- Clean __pycache__ from tracked areas
- Generate cleanup manifest
- Safety: Never delete, only move to archive/

Usage:
    python sanitizer.py [--dry-run]
"""

import argparse
import os
import shutil
import glob
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.resolve()
ARCHIVE_DIR = BASE_DIR / "archive" / "cleanup"
MANIFEST_FILE = ARCHIVE_DIR / f"manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

# Patterns to archive by category
ARCHIVE_PATTERNS = {
    "fix_scripts": [
        "fix_search*.py",
        "fix_persona*.py",
        "fix_ctransformers_issue.py",
        "fix_encoding.py",
        "fix_kuera_syntax.py",
        "fix_llm_serving_nusantara.py",
        "fix_uploaded_files.py",
    ],
    "download_scripts": [
        "download_all_models.py",
        "download_auto.py",
        "download_bartowski_models.py",
        "download_hf_new_cli.py",
        "download_models.py",
        "download_models_simple.py",
        "download_models_smart.py",
        "download_priorities.py",
        "download_progressive.py",
        "download_simple.py",
    ],
    "chat_scripts": [
        "kuera_chat.py",
        "kuera_chat_demo.py",
        "kuera_chat_improved.py",
        "kuera_chat_simple.py",
        "kuera_human_like.py",
        "kuera_qwen_chat.py",
        "kuera_smart_chat.py",
        "kuera_ultimate_chat.py",
    ],
    "web_server_old": [
        "kuera_web_server.py",
        "kuwera_web_server.py",
        "kuwera_web_interface.py",
        "web_interface.py",
    ],
    "test_scripts_root": [
        "test_api.py",
        "test_chat_page.py",
        "test_dashboard.py",
        "test_direct.py",
        "test_qwen_indonesian.py",
        "test_smart_chat.py",
    ],
    "demo_scripts": [
        "demo_7day_evolusi.py",
        "demo_agent.py",
        "demo_alignment.py",
        "demo_loop.py",
        "demo_nusantara.py",
        "demo_real_evolution.py",
    ],
    "integrate_scripts": [
        "integrate_all_new_models.py",
        "integrate_bartowski_models.py",
        "integrate_models.py",
    ],
    "analyze_scripts": [
        "analyze_indonesia.py",
        "analyze_kalimantan.py",
        "quick_analyze.py",
        "kalimantan_bps_simulation.py",
    ],
    "persona_patches": [
        "persona_*.py",
    ],
    "redundant_bots": [
        "bot_telegram*.py",
        "bot_discord*.py",
    ],
}

# Files to NEVER touch (actively used by services.yaml or main.py)
PROTECTED_FILES = {
    "main.py",
    "gateway_server.py",
    "start_api.py",
    "start_dashboard.py",
    "kuwera_web_server_v2.py",
    "kuera_integrated_system.py",
    "kuera_evolution_engine.py",
    "template_master.py",
    "audit_toolkit.py",
    "template_audit_spi.py",
    "template_audit_kinerja.py",
    "pdf_extractor.py",
    "file_processor.py",
    "sanitizer.py",
}


def should_archive(filepath: Path) -> bool:
    """Check if file should be archived (not protected)."""
    if filepath.name in PROTECTED_FILES:
        return False
    # Don't archive files inside src/ or tests/ or app/ (those are managed)
    rel = filepath.relative_to(BASE_DIR)
    if str(rel).startswith(("src/", "tests/", "app/", "admin_panel/", "scripts/", "config/", "data/", "models/", "docs/")):
        return False
    return True


def run_sanitizer(dry_run: bool = False):
    print("=" * 60)
    print("KUERA WORKSPACE SANITIZER")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Base: {BASE_DIR}")
    print("=" * 60)

    manifest_lines = [
        "# KUERA Cleanup Manifest\n",
        f"Date: {datetime.now().isoformat()}\n",
        f"Mode: {'dry_run' if dry_run else 'live'}\n\n",
    ]

    total_archived = 0
    total_size = 0

    for category, patterns in ARCHIVE_PATTERNS.items():
        category_dir = ARCHIVE_DIR / category
        if not dry_run:
            category_dir.mkdir(parents=True, exist_ok=True)

        archived_in_category = []

        for pattern in patterns:
            for filepath in BASE_DIR.glob(pattern):
                if not filepath.is_file():
                    continue
                if not should_archive(filepath):
                    print(f"  [SKIP - PROTECTED] {filepath.name}")
                    continue

                dest = category_dir / filepath.name
                size = filepath.stat().st_size

                if dry_run:
                    print(f"  [DRY] Would archive: {filepath.name} -> archive/cleanup/{category}/")
                else:
                    shutil.move(str(filepath), str(dest))
                    print(f"  [MOVED] {filepath.name} -> archive/cleanup/{category}/")

                archived_in_category.append({
                    "file": filepath.name,
                    "size": size,
                    "to": f"archive/cleanup/{category}/"
                })
                total_archived += 1
                total_size += size

        if archived_in_category:
            manifest_lines.append(f"## {category}\n")
            for item in archived_in_category:
                manifest_lines.append(f"- `{item['file']}` ({item['size']:,} bytes) -> `{item['to']}`\n")
            manifest_lines.append("\n")

    # Clean __pycache__ in root (not in src/ since those are managed)
    pycache_dirs = list(BASE_DIR.glob("__pycache__")) + list(BASE_DIR.glob("*.pyc"))
    if pycache_dirs:
        manifest_lines.append("## Python Cache Cleanup\n")
        for p in pycache_dirs:
            if dry_run:
                print(f"  [DRY] Would remove: {p.name}")
            else:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                print(f"  [REMOVED] {p.name}")
            manifest_lines.append(f"- Removed `{p.name}`\n")
        manifest_lines.append("\n")

    # Summary
    summary = (
        f"## Summary\n\n"
        f"- **Total files archived:** {total_archived}\n"
        f"- **Total size freed:** {total_size:,} bytes ({total_size / 1024:.1f} KB)\n"
        f"- **Archive location:** `archive/cleanup/`\n\n"
        f"To restore any file:\n"
        f"```bash\n"
        f"mv archive/cleanup/<category>/<file> .\n"
        f"```\n"
    )
    manifest_lines.append(summary)

    if not dry_run:
        MANIFEST_FILE.write_text("".join(manifest_lines), encoding="utf-8")
        print(f"\n📄 Manifest written: {MANIFEST_FILE}")

    print("\n" + "=" * 60)
    print(f"Done. Files {'would be' if dry_run else ''} archived: {total_archived}")
    print(f"Space {'would be' if dry_run else ''} moved: {total_size / 1024:.1f} KB")
    if not dry_run:
        print(f"Manifest: {MANIFEST_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KUERA Workspace Sanitizer")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    args = parser.parse_args()
    run_sanitizer(dry_run=args.dry_run)
