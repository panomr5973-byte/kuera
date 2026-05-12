"""Tests for PDF report generation."""

import pytest
import sys
from pathlib import Path
import tempfile
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))


def test_pdf_report_init():
    from audit_toolkit import PDFReport
    report = PDFReport(title="Test Report")
    assert report.title == "Test Report"


def test_pdf_report_generate():
    from audit_toolkit import PDFReport, FPDF_AVAILABLE
    if not FPDF_AVAILABLE:
        pytest.skip("fpdf not installed")
    
    report = PDFReport(title="Test Audit Report")
    df = pd.DataFrame({
        'ROA': [5.0, 3.2, 8.1, 2.5],
        'ROE': [10.0, 6.5, 15.2, 4.1],
    })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_report.pdf"
        report.generate(df, str(output_path))
        assert output_path.exists()
        assert output_path.stat().st_size > 0


def test_pdf_report_generate_empty_df():
    from audit_toolkit import PDFReport, FPDF_AVAILABLE
    if not FPDF_AVAILABLE:
        pytest.skip("fpdf not installed")
    
    report = PDFReport()
    df = pd.DataFrame()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "empty_report.pdf"
        report.generate(df, str(output_path))
        assert output_path.exists()
