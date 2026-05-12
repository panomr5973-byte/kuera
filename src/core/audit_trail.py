"""KUERA AI — Audit Trail Database.

Structured SQLite logging for every audit run.
Schema: audit_runs(id, timestamp, jenis, filename, status, output_path,
                   summary_json, chart_json, client_ip, duration_ms)
"""

import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

BASE_DIR = Path(__file__).parent.parent.parent.resolve()
DB_PATH = BASE_DIR / "data" / "audit_log.db"


def _get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row factory."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the audit_runs table if it doesn't exist."""
    conn = _get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                jenis TEXT NOT NULL,
                filename TEXT NOT NULL,
                status TEXT NOT NULL,
                output_path TEXT,
                summary_json TEXT,
                chart_json TEXT,
                client_ip TEXT,
                duration_ms INTEGER
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_runs_jenis ON audit_runs(jenis)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_runs_timestamp ON audit_runs(timestamp)"
        )
        conn.commit()
    finally:
        conn.close()


def log_audit_run(
    jenis: str,
    filename: str,
    status: str,
    output_path: Optional[str] = None,
    summary: Optional[Dict] = None,
    charts: Optional[List[Dict]] = None,
    client_ip: Optional[str] = None,
    duration_ms: Optional[int] = None,
) -> int:
    """Log a single audit run. Returns the inserted row id."""
    init_db()
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO audit_runs
            (timestamp, jenis, filename, status, output_path,
             summary_json, chart_json, client_ip, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                jenis,
                filename,
                status,
                output_path,
                json.dumps(summary, default=str) if summary else None,
                json.dumps(charts, default=str) if charts else None,
                client_ip,
                duration_ms,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_history(
    jenis: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """Get paginated audit history, optionally filtered by jenis."""
    init_db()
    conn = _get_connection()
    try:
        if jenis:
            rows = conn.execute(
                """
                SELECT id, timestamp, jenis, filename, status, output_path,
                       summary_json, client_ip, duration_ms
                FROM audit_runs
                WHERE jenis = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                """,
                (jenis, limit, offset),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, timestamp, jenis, filename, status, output_path,
                       summary_json, client_ip, duration_ms
                FROM audit_runs
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()

        results = []
        for row in rows:
            summary = None
            if row["summary_json"]:
                try:
                    summary = json.loads(row["summary_json"])
                except json.JSONDecodeError:
                    summary = None
            results.append(
                {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "jenis": row["jenis"],
                    "filename": row["filename"],
                    "status": row["status"],
                    "output_path": row["output_path"],
                    "summary": summary,
                    "client_ip": row["client_ip"],
                    "duration_ms": row["duration_ms"],
                }
            )
        return results
    finally:
        conn.close()


def get_run_by_id(run_id: int) -> Optional[Dict[str, Any]]:
    """Get a single audit run by id."""
    init_db()
    conn = _get_connection()
    try:
        row = conn.execute(
            """
            SELECT id, timestamp, jenis, filename, status, output_path,
                   summary_json, chart_json, client_ip, duration_ms
            FROM audit_runs
            WHERE id = ?
            """,
            (run_id,),
        ).fetchone()

        if row is None:
            return None

        summary = None
        charts = None
        if row["summary_json"]:
            try:
                summary = json.loads(row["summary_json"])
            except json.JSONDecodeError:
                pass
        if row["chart_json"]:
            try:
                charts = json.loads(row["chart_json"])
            except json.JSONDecodeError:
                pass

        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "jenis": row["jenis"],
            "filename": row["filename"],
            "status": row["status"],
            "output_path": row["output_path"],
            "summary": summary,
            "charts": charts,
            "client_ip": row["client_ip"],
            "duration_ms": row["duration_ms"],
        }
    finally:
        conn.close()


def delete_run(run_id: int) -> bool:
    """Delete a single audit run by id. Returns True if deleted."""
    init_db()
    conn = _get_connection()
    try:
        cursor = conn.execute("DELETE FROM audit_runs WHERE id = ?", (run_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
