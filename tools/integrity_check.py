#!/usr/bin/env python3
"""KUERA AI — Integrity Check Engine (Self-Auditing)

Monitors workspace health and detects entropy increase.
Run periodically or after major changes.

Usage:
    python tools/integrity_check.py [--fix]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

BASE_DIR = Path(__file__).parent.parent.resolve()
MANIFEST_PATH = BASE_DIR / "KUERA_MANIFEST.json"
MEMORY_DIR = BASE_DIR / "memory"


def load_manifest() -> dict:
    """Load KUERA_MANIFEST.json."""
    if not MANIFEST_PATH.exists():
        return {}
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load manifest: {e}")
        return {}


def count_root_py_files() -> int:
    """Count .py files directly in root (excluding protected)."""
    return len(list(BASE_DIR.glob("*.py")))


def find_untracked_py() -> List[str]:
    """Find .py files in root not listed in manifest."""
    manifest = load_manifest()
    
    # Collect all known files from manifest
    known = set()
    
    # Active modules
    active = set(manifest.get("active_modules", {}).values())
    known.update(Path(a).name for a in active)
    
    # Deprecated modules
    deprecated = manifest.get("deprecated_modules", {})
    for desc in deprecated.values():
        if " — " in desc:
            fname = desc.split(" — ")[0].strip()
            known.add(fname)
    
    # Utilities
    utilities = manifest.get("utilities", {})
    for util_list in utilities.values():
        known.update(util_list)
    
    # Always protect core files
    protected = {
        "main.py", "gateway_server.py", "sanitizer.py",
        "audit_toolkit.py", "template_audit_spi.py",
        "template_audit_kinerja.py", "template_master.py",
        "pdf_extractor.py", "file_processor.py",
        "kuera_integrated_system.py", "kuwera_web_server_v2.py",
        "kuera_evolution_engine.py", "start_api.py", "start_dashboard.py",
        "KUERA_MANIFEST.json",
    }
    known.update(protected)
    
    untracked = []
    for py_file in BASE_DIR.glob("*.py"):
        if py_file.name not in known:
            untracked.append(py_file.name)
    return untracked


def find_anti_patterns() -> List[Dict]:
    """Scan root for anti-pattern files."""
    patterns = []
    
    # Fix spiral
    fix_files = [f.name for f in BASE_DIR.glob("fix_*.py")]
    if fix_files:
        patterns.append({
            "pattern": "Fix Spiral",
            "files": fix_files,
            "severity": "CRITICAL",
            "message": f"{len(fix_files)} fix_*.py detected. Edit existing files instead."
        })
    
    # Versioning by filename (exclude files referenced in services.yaml)
    services_yaml = BASE_DIR / "config" / "services.yaml"
    services_refs = set()
    if services_yaml.exists():
        try:
            content = services_yaml.read_text(encoding="utf-8")
            # Extract script references
            import re
            for m in re.finditer(r'script:\s*"([^"]+\.py)"', content):
                services_refs.add(Path(m.group(1)).name)
        except Exception:
            pass
    
    versioned = []
    for f in BASE_DIR.glob("*_v2.py"):
        if f.name not in services_refs:
            versioned.append(f.name)
    for f in BASE_DIR.glob("*_v3.py"):
        if f.name not in services_refs:
            versioned.append(f.name)
    
    if versioned:
        patterns.append({
            "pattern": "Version Sprawl",
            "files": versioned,
            "severity": "HIGH",
            "message": f"{len(versioned)} versioned files detected. Use git for versioning."
        })
    
    # Download obsession
    download_files = [f.name for f in BASE_DIR.glob("download_*.py")]
    if len(download_files) > 2:
        patterns.append({
            "pattern": "Download Obsession",
            "files": download_files,
            "severity": "HIGH",
            "message": f"{len(download_files)} download scripts. Consolidate into one manager."
        })
    
    # Chat proliferation
    chat_files = [f.name for f in BASE_DIR.glob("kuera_chat*.py")] + [f.name for f in BASE_DIR.glob("kuwera_chat*.py")]
    if len(chat_files) > 2:
        patterns.append({
            "pattern": "Chat Proliferation",
            "files": chat_files,
            "severity": "HIGH",
            "message": f"{len(chat_files)} chat scripts. Refine existing, don't spawn new."
        })
    
    return patterns


def find_hardcoded_paths() -> List[Dict]:
    """Scan src/ and tools/ for hardcoded Windows paths."""
    issues = []
    path_pattern = re.compile(r'[\"\']([A-Za-z]:[\\/][^\"\']+)[\"\']')
    
    scan_dirs = [BASE_DIR / "src", BASE_DIR / "tools", BASE_DIR / "scripts"]
    
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                matches = path_pattern.findall(content)
                # Filter out legitimate patterns (like __file__ based paths)
                real_hardcoded = []
                for m in matches:
                    # Skip if it contains variables or f-strings
                    if "{" in m or "}" in m:
                        continue
                    # Skip if it's just a drive reference in a comment
                    if m.count("\\") < 2 and m.count("/") < 2:
                        continue
                    real_hardcoded.append(m)
                
                if real_hardcoded:
                    issues.append({
                        "file": str(py_file.relative_to(BASE_DIR)),
                        "paths": real_hardcoded[:3]  # Limit to first 3
                    })
            except Exception:
                pass
    
    return issues


def check_manifest_compliance() -> Tuple[int, List[str]]:
    """Check if workspace follows manifest rules."""
    manifest = load_manifest()
    if not manifest:
        return 0, ["[FAIL] KUERA_MANIFEST.json not found or unreadable"]
    
    issues = []
    score = 100
    
    # Check 1: Root .py count
    root_py = count_root_py_files()
    max_allowed = manifest.get("entropy_thresholds", {}).get("max_root_py_files", 25)
    if root_py > max_allowed:
        issues.append(f"[WARN] Root has {root_py} .py files (max: {max_allowed})")
        score -= 10
    else:
        issues.append(f"[OK] Root has {root_py} .py files (max: {max_allowed})")
    
    # Check 2: Untracked files
    untracked = find_untracked_py()
    if untracked:
        issues.append(f"[WARN] {len(untracked)} untracked .py in root: {', '.join(untracked[:5])}")
        score -= 15
    else:
        issues.append("[OK] No untracked .py files in root")
    
    # Check 3: Anti-patterns
    anti_patterns = find_anti_patterns()
    for ap in anti_patterns:
        severity_penalty = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 10}.get(ap["severity"], 5)
        issues.append(f"[{ap['severity']}] {ap['message']}")
        score -= severity_penalty
    
    if not anti_patterns:
        issues.append("[OK] No anti-patterns detected")
    
    # Check 4: Hardcoded paths
    hardcoded = find_hardcoded_paths()
    if hardcoded:
        issues.append(f"[WARN] Hardcoded paths in {len(hardcoded)} files")
        for h in hardcoded[:3]:
            issues.append(f"       {h['file']}: {h['paths']}")
        score -= 10
    else:
        issues.append("[OK] No hardcoded paths detected")
    
    # Check 5: Manifest version
    version = manifest.get("version", "unknown")
    phase = manifest.get("phase", 0)
    issues.append(f"[INFO] Manifest version: {version} | Phase: {phase}")
    
    return max(0, score), issues


def write_report(score: int, issues: List[str], fix: bool = False):
    """Write integrity report to memory and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    status = "HEALTHY" if score >= 80 else "DEGRADED" if score >= 50 else "CRITICAL"
    
    lines = [
        f"# KUERA Integrity Check Report\n",
        f"**Date:** {timestamp}\n",
        f"**Score:** {score}/100\n",
        f"**Status:** {status}\n\n",
        "## Findings\n\n",
    ]
    
    for issue in issues:
        lines.append(f"- {issue}\n")
    
    lines.append("\n## Recommendations\n\n")
    
    if score < 100:
        lines.append("- Run `python sanitizer.py --dry-run` to preview cleanup\n")
    if score < 80:
        lines.append("- Address anti-patterns immediately\n")
    if score < 50:
        lines.append("- **CRITICAL**: System entropy too high. Cleanup required before new features.\n")
    
    lines.append("\n---\n")
    
    report_text = "".join(lines)
    print("\n" + "=" * 60)
    print(report_text)
    print("=" * 60)
    
    # Save to memory
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    report_path = MEMORY_DIR / f"integrity_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(report_text, encoding="utf-8")
    print(f"\n📄 Report saved: {report_path}")
    
    # Also log via logger_engine if available
    try:
        sys.path.insert(0, str(BASE_DIR))
        from src.core.logger_engine import log_activity
        log_activity(f"Integrity check: {status} ({score}/100)", {"issues_count": len(issues)})
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="KUERA Integrity Check")
    parser.add_argument("--fix", action="store_true", help="Suggest fixes (not auto-apply)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("KUERA INTEGRITY CHECK")
    print(f"Base: {BASE_DIR}")
    print("=" * 60)
    
    score, issues = check_manifest_compliance()
    write_report(score, issues, fix=args.fix)
    
    if score < 50:
        print("\n⚠️  CRITICAL entropy detected. Run sanitizer.py immediately.")
        sys.exit(1)
    elif score < 80:
        print("\n⚠️  DEGRADED. Address warnings before continuing development.")
        sys.exit(0)
    else:
        print("\n✅ System healthy. Proceed with confidence.")
        sys.exit(0)


if __name__ == "__main__":
    main()
