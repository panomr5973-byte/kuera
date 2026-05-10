"""Tests for Audit Toolkit connector."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.data.audit_connector import list_uploaded_files


def test_list_uploaded_files_returns_list():
    files = list_uploaded_files()
    assert isinstance(files, list)
