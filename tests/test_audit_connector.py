"""Tests for Audit Toolkit connector."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.data.audit_connector import list_uploaded_files, list_templates, analyze_excel


def test_list_uploaded_files_returns_list():
    files = list_uploaded_files()
    assert isinstance(files, list)


def test_list_templates_returns_list():
    templates = list_templates()
    assert isinstance(templates, list)
    assert len(templates) == 3


def test_analyze_excel_missing_file():
    result = analyze_excel("/path/that/does/not/exist.xlsx")
    assert result["status"] == "error"
