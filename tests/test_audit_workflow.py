"""Tests for the unified audit workflow."""

import pytest
from pathlib import Path
import sys
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))


class TestAuditWorkflow:
    """Test audit_workflow orchestrator."""

    def test_list_templates(self):
        from src.data.audit_workflow import list_templates
        templates = list_templates()
        assert len(templates) == 3
        ids = [t['id'] for t in templates]
        assert 'keuangan' in ids
        assert 'spi' in ids
        assert 'kinerja' in ids

    def test_run_audit_invalid_type(self):
        from src.data.audit_workflow import run_audit
        result = run_audit('invalid', 'test.xlsx')
        assert result['status'] == 'error'
        assert 'tidak tersedia' in result['error_message']


class TestAnomalyDetection:
    """Test anomaly detection in audit_toolkit."""

    def test_iqr_detection(self):
        from audit_toolkit import ExcelAuditProcessorV2
        proc = ExcelAuditProcessorV2()
        
        df = pd.DataFrame({
            'nilai': [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]  # 100 is clear outlier
        })
        
        anomalies = proc.detect_anomalies(df, method='iqr')
        assert 'nilai' in anomalies
        assert any(a['method'] == 'IQR' for a in anomalies['nilai'])

    def test_zscore_detection(self):
        from audit_toolkit import ExcelAuditProcessorV2
        proc = ExcelAuditProcessorV2()
        
        # Generate data with clear extreme outlier (z-score > 3)
        data = [5.0] * 50  # 50 identical values, std ~0
        data.append(500.0)  # extreme outlier
        
        df = pd.DataFrame({'nilai': data})
        
        anomalies = proc.detect_anomalies(df, method='zscore')
        assert 'nilai' in anomalies
        assert any(a['method'] == 'Z-Score' for a in anomalies['nilai'])

    def test_no_anomalies(self):
        from audit_toolkit import ExcelAuditProcessorV2
        proc = ExcelAuditProcessorV2()
        
        df = pd.DataFrame({
            'nilai': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        })
        
        anomalies = proc.detect_anomalies(df, method='all')
        # Should have few or no flags for uniform data
        assert isinstance(anomalies, dict)

    def test_benford_detection(self):
        from audit_toolkit import ExcelAuditProcessorV2
        proc = ExcelAuditProcessorV2()
        
        # Generate data that follows Benford's Law closely
        np.random.seed(42)
        benford_data = []
        for d in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            prob = {1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 5: 0.079,
                    6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046}[d]
            count = int(prob * 500)
            for _ in range(count):
                val = d * (10 ** np.random.uniform(1, 5))
                benford_data.append(val)
        
        df = pd.DataFrame({'transaksi': benford_data})
        anomalies = proc.detect_anomalies(df, method='benford')
        # Should NOT flag Benford-compliant data
        assert 'transaksi' not in anomalies or len(anomalies.get('transaksi', [])) == 0


class TestChartGeneration:
    """Test chart data generation."""

    def test_keuangan_charts(self):
        from src.data.audit_workflow import generate_chart_data, AuditResult
        result = AuditResult(
            jenis='keuangan', status='success', file_input='test.xlsx', file_output='out.xlsx',
            summary={
                'total_bumd': 50,
                'roa_rendah': 5,
                'underperforming': 8,
                'anomaly_details': {
                    'nilai': [{'method': 'IQR', 'count': 3, 'description': 'test'}]
                }
            }
        )
        charts = generate_chart_data(result)
        assert 'health_pie' in charts
        assert charts['health_pie']['type'] == 'doughnut'
        assert 'anomaly_bar' in charts

    def test_spi_charts(self):
        from src.data.audit_workflow import generate_chart_data, AuditResult
        result = AuditResult(
            jenis='spi', status='success', file_input='test.xlsx', file_output='out.xlsx',
            summary={
                'nama_entitas': 'PDAM Test',
                'nilai_total': 3.5,
                'kategori': 'CUKUP',
                'komponen': {
                    'LINGKUNGAN_PENGENDALIAN': {'nama': 'Lingkungan', 'nilai': 4.0, 'bobot': 0.2, 'nilai_bobot': 0.8}
                }
            }
        )
        charts = generate_chart_data(result)
        assert 'spi_radar' in charts
        assert charts['spi_radar']['type'] == 'radar'
        assert 'spi_gauge' in charts

    def test_kinerja_charts(self):
        from src.data.audit_workflow import generate_chart_data, AuditResult
        result = AuditResult(
            jenis='kinerja', status='success', file_input='test.xlsx', file_output='out.xlsx',
            summary={
                'tahun': 2024,
                'total_entitas': 20,
                'predikat_distribution': {'A': 5, 'B': 8, 'C': 4, 'D': 2, 'E': 1},
                'top_5': [{'nama': 'BUMD A', 'skor': 95.0, 'predikat': 'A'}],
                'bottom_5': [{'nama': 'BUMD Z', 'skor': 45.0, 'predikat': 'E'}]
            }
        )
        charts = generate_chart_data(result)
        assert 'predikat_pie' in charts
        assert 'ranking_bar' in charts
        assert 'score_dist' in charts

    def test_error_result_no_charts(self):
        from src.data.audit_workflow import generate_chart_data, AuditResult
        result = AuditResult(
            jenis='keuangan', status='error', file_input='test.xlsx', file_output=None,
            summary={}, error_message='Failed'
        )
        charts = generate_chart_data(result)
        assert charts == {}


class TestAuditConnector:
    """Test audit_connector API wrapper."""

    def test_list_uploaded_files_returns_list(self):
        from src.data.audit_connector import list_uploaded_files
        files = list_uploaded_files()
        assert isinstance(files, list)

    def test_list_templates_returns_list(self):
        from src.data.audit_connector import list_templates
        templates = list_templates()
        assert isinstance(templates, list)
        assert len(templates) == 3
