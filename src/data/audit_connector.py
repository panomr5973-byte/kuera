"""KUERA AI — Audit Toolkit Connector.

Wraps the legacy audit_toolkit.py and audit_workflow.py to provide a clean API for the dashboard.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import sys

BASE_DIR = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

# Lazy import to avoid loading heavy deps at startup
_audit_toolkit = None
_audit_workflow = None


def _get_toolkit():
    global _audit_toolkit
    if _audit_toolkit is None:
        try:
            import audit_toolkit
            _audit_toolkit = audit_toolkit.ExcelAuditProcessorV2()
        except Exception as e:
            return None, str(e)
    return _audit_toolkit, None


def _get_workflow():
    global _audit_workflow
    if _audit_workflow is None:
        try:
            # Import from src.data since audit_workflow lives there
            from src.data import audit_workflow
            _audit_workflow = audit_workflow
        except Exception as e:
            return None, str(e)
    return _audit_workflow, None


def analyze_excel(filepath: str) -> Dict:
    """Analyze an Excel file and return summary statistics.

    Args:
        filepath: Path to the Excel file.

    Returns:
        Dict with summary, columns, row_count, anomalies, and status.
    """
    toolkit, error = _get_toolkit()
    if toolkit is None:
        return {"status": "error", "message": error}

    try:
        df = toolkit.read_excel_multiheader(filepath)
        if df is None:
            return {"status": "error", "message": "Failed to read Excel file"}

        toolkit.detect_and_convert_numbers(df)

        # Basic summary
        summary = {
            "status": "success",
            "file": Path(filepath).name,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": {str(c): str(df[c].dtype) for c in df.columns},
        }

        # Anomaly detection
        if hasattr(toolkit, 'detect_anomalies'):
            try:
                anomalies = toolkit.detect_anomalies(df)
                summary["anomalies"] = anomalies
                summary["anomaly_count"] = sum(len(v) for v in anomalies.values())
            except Exception:
                summary["anomalies"] = {}
                summary["anomaly_count"] = 0
        else:
            summary["anomalies"] = {}
            summary["anomaly_count"] = 0

        # Numeric summary
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        summary["numeric_columns"] = numeric_cols
        if numeric_cols:
            desc = df[numeric_cols].describe().to_dict()
            summary["statistics"] = desc

        return summary

    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_audit(jenis: str, filepath: str, **kwargs) -> Dict:
    """Run a specific audit workflow.
    
    Args:
        jenis: 'keuangan', 'spi', or 'kinerja'
        filepath: Path to input Excel file
        **kwargs: Additional parameters (e.g., nama_entitas, tahun)
    
    Returns:
        Dict with audit results
    """
    workflow, error = _get_workflow()
    if workflow is None:
        return {"status": "error", "message": f"audit_workflow not available: {error}"}
    
    try:
        result = workflow.run_audit(jenis, filepath, **kwargs)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_templates() -> List[Dict]:
    """List available audit templates."""
    workflow, error = _get_workflow()
    if workflow is None:
        return []
    try:
        return workflow.list_templates()
    except Exception:
        return []


def list_uploaded_files() -> List[str]:
    """List Excel files available for analysis."""
    upload_dir = BASE_DIR / "data" / "uploads"
    if not upload_dir.exists():
        return []
    files = list(upload_dir.glob("*.xlsx")) + list(upload_dir.glob("*.xls"))
    return [f.name for f in files]
