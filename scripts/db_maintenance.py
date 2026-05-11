#!/usr/bin/env python3
"""KUERA AI — Database Maintenance Script.

Performs SQLite optimization:
- VACUUM to reclaim space
- ANALYZE for query planner
- Add indexes for frequent queries
- Archive old records (> 90 days)
- Report size changes

Usage:
    python scripts/db_maintenance.py [--archive-days 90] [--dry-run]
"""

import argparse
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
ARCHIVE_DIR = DATA_DIR / "archive"
LOGS_DIR = BASE_DIR / "logs"

# Database files to maintain
DB_FILES = [
    (DATA_DIR / "kuera_database.db", "main"),
    (DATA_DIR / "kuwera_memory.db", "memory"),
    (DATA_DIR / "kuera_evolution.db", "evolution"),
    (LOGS_DIR / "feedback" / "self_improve.db", "feedback"),
]

# Indexes to ensure exist (table_name, index_name, columns)
RECOMMENDED_INDEXES = {
    "interactions": [
        ("idx_interactions_timestamp", "timestamp"),
        ("idx_interactions_session", "session_id"),
        ("idx_interactions_user", "user_id"),
    ],
    "uploaded_files": [
        ("idx_uploaded_category", "category"),
        ("idx_uploaded_processed", "processed"),
    ],
    "knowledge_chunks": [
        ("idx_chunks_fileid", "file_id"),
    ],
    "sessions": [
        ("idx_sessions_user", "user_id"),
        ("idx_sessions_active", "is_active"),
    ],
    "analytics_daily": [
        ("idx_analytics_date", "date"),
    ],
}


def get_db_size(db_path: Path) -> int:
    """Return file size in bytes."""
    return db_path.stat().st_size if db_path.exists() else 0


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def vacuum_db(db_path: Path, dry_run: bool = False) -> dict:
    """Run VACUUM and ANALYZE on a SQLite database."""
    result = {
        "file": str(db_path),
        "before_size": 0,
        "after_size": 0,
        "saved": 0,
        "status": "skipped"
    }
    
    if not db_path.exists():
        result["status"] = "not_found"
        return result
    
    result["before_size"] = get_db_size(db_path)
    
    if dry_run:
        result["status"] = "dry_run"
        return result
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Run optimize pragmas
        cursor.execute("PRAGMA optimize")
        cursor.execute("VACUUM")
        cursor.execute("ANALYZE")
        
        conn.close()
        
        result["after_size"] = get_db_size(db_path)
        result["saved"] = result["before_size"] - result["after_size"]
        result["status"] = "success"
        
    except Exception as e:
        result["status"] = f"error: {e}"
    
    return result


def add_indexes(db_path: Path, dry_run: bool = False) -> list:
    """Add recommended indexes if they don't exist."""
    results = []
    
    if not db_path.exists():
        return results
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}
        
        for table, indexes in RECOMMENDED_INDEXES.items():
            if table not in tables:
                continue
            
            for idx_name, columns in indexes:
                # Check if index already exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name=?;",
                    (idx_name,)
                )
                if cursor.fetchone():
                    results.append({"index": idx_name, "status": "already_exists"})
                    continue
                
                if dry_run:
                    results.append({"index": idx_name, "status": "dry_run"})
                    continue
                
                try:
                    cursor.execute(f"CREATE INDEX {idx_name} ON {table}({columns});")
                    results.append({"index": idx_name, "status": "created"})
                except Exception as e:
                    results.append({"index": idx_name, "status": f"error: {e}"})
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        results.append({"index": "general", "status": f"error: {e}"})
    
    return results


def archive_old_records(db_path: Path, archive_days: int, dry_run: bool = False) -> dict:
    """Archive records older than archive_days from interactions table."""
    result = {
        "file": str(db_path),
        "archived_rows": 0,
        "status": "skipped"
    }
    
    if not db_path.exists():
        result["status"] = "not_found"
        return result
    
    cutoff = datetime.now() - timedelta(days=archive_days)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if interactions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions';")
        if not cursor.fetchone():
            result["status"] = "no_interactions_table"
            conn.close()
            return result
        
        # Count old records
        cursor.execute(
            "SELECT COUNT(*) FROM interactions WHERE timestamp < ?;",
            (cutoff_str,)
        )
        old_count = cursor.fetchone()[0]
        
        if old_count == 0:
            result["status"] = "no_old_records"
            conn.close()
            return result
        
        result["archived_rows"] = old_count
        
        if dry_run:
            result["status"] = "dry_run"
            conn.close()
            return result
        
        # Archive to separate DB
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        archive_file = ARCHIVE_DIR / f"interactions_archive_{datetime.now().strftime('%Y%m%d')}.db"
        
        # Create archive DB with same schema
        archive_conn = sqlite3.connect(str(archive_file))
        archive_cursor = archive_conn.cursor()
        
        # Get schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='interactions';")
        schema = cursor.fetchone()[0]
        archive_cursor.execute(schema)
        
        # Copy old records
        cursor.execute(
            "SELECT * FROM interactions WHERE timestamp < ?;",
            (cutoff_str,)
        )
        rows = cursor.fetchall()
        
        # Get column count for placeholder
        col_count = len(rows[0]) if rows else 0
        placeholders = ",".join(["?"] * col_count)
        
        archive_cursor.executemany(
            f"INSERT INTO interactions VALUES ({placeholders})",
            rows
        )
        archive_conn.commit()
        archive_conn.close()
        
        # Delete from main DB
        cursor.execute(
            "DELETE FROM interactions WHERE timestamp < ?;",
            (cutoff_str,)
        )
        conn.commit()
        conn.close()
        
        # Vacuum after deletion
        vacuum_db(db_path)
        
        result["status"] = "success"
        result["archive_file"] = str(archive_file)
        
    except Exception as e:
        result["status"] = f"error: {e}"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="KUERA Database Maintenance")
    parser.add_argument("--archive-days", type=int, default=90, help="Archive records older than N days")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    args = parser.parse_args()
    
    print("=" * 60)
    print("KUERA DATABASE MAINTENANCE")
    print(f"Dry run: {args.dry_run}")
    print("=" * 60)
    
    total_before = 0
    total_after = 0
    total_saved = 0
    
    # Process each database
    for db_path, label in DB_FILES:
        print(f"\n📁 {label}: {db_path}")
        
        if not db_path.exists():
            print("   ⚠️  File not found, skipping")
            continue
        
        # Backup before maintenance
        if not args.dry_run:
            backup_path = db_path.with_suffix(".db.bak")
            shutil.copy2(db_path, backup_path)
            print(f"   💾 Backup created: {backup_path.name}")
        
        # Vacuum
        vac_result = vacuum_db(db_path, dry_run=args.dry_run)
        total_before += vac_result["before_size"]
        total_after += vac_result["after_size"]
        total_saved += vac_result["saved"]
        
        if vac_result["status"] == "success":
            print(f"   ✓ VACUUM: {format_size(vac_result['saved'])} reclaimed")
        elif vac_result["status"] == "dry_run":
            print(f"   ⏸️  VACUUM: dry run")
        else:
            print(f"   ⚠️  VACUUM: {vac_result['status']}")
        
        # Add indexes
        idx_results = add_indexes(db_path, dry_run=args.dry_run)
        created = sum(1 for r in idx_results if r["status"] == "created")
        if created > 0:
            print(f"   ✓ Indexes: {created} created")
        
        # Archive old records (only for main DB)
        if label == "main":
            arch_result = archive_old_records(db_path, args.archive_days, dry_run=args.dry_run)
            if arch_result["status"] == "success":
                print(f"   ✓ Archive: {arch_result['archived_rows']} rows archived")
                print(f"   📦 Archive file: {arch_result.get('archive_file', 'N/A')}")
            elif arch_result["status"] == "dry_run" and arch_result["archived_rows"] > 0:
                print(f"   ⏸️  Archive: {arch_result['archived_rows']} rows would be archived")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total size before: {format_size(total_before)}")
    print(f"Total size after:  {format_size(total_after)}")
    print(f"Space reclaimed:   {format_size(total_saved)}")
    
    if not args.dry_run:
        print("\n✅ Maintenance complete. Backups created with .db.bak extension.")
        print("   To restore: copy .db.bak back to original filename")
    else:
        print("\n⏸️  Dry run complete. No changes made.")


if __name__ == "__main__":
    main()
