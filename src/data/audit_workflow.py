"""KUERA AI — Unified Audit Workflow Orchestrator.

Integrates three audit templates into a single callable workflow:
- Audit Keuangan (financial ratios, BUMD analysis)
- Audit SPI (COSO internal control framework)
- Audit Kinerja (performance scoring & ranking)
"""

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from src.utils.cache import ttl_cache

BASE_DIR = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from src.core.audit_trail import log_audit_run


@dataclass
class AuditResult:
    """Standardized audit result container."""
    jenis: str
    status: str  # success | error
    file_input: str
    file_output: Optional[str]
    summary: Dict[str, Any]
    details: Optional[Dict] = None
    error_message: Optional[str] = None


def _safe_import(module_name: str):
    """Lazy import with error handling."""
    try:
        return __import__(module_name)
    except ImportError as e:
        return None


def run_audit_keuangan(filepath: str, output_dir: Optional[str] = None) -> AuditResult:
    """Run financial audit on an Excel file.
    
    Args:
        filepath: Path to Excel file with BUMD/financial data
        output_dir: Directory to save output files (default: same as input)
    
    Returns:
        AuditResult with summary and paths to generated files
    """
    audit_toolkit = _safe_import('audit_toolkit')
    if audit_toolkit is None:
        return AuditResult(
            jenis='keuangan', status='error', file_input=filepath,
            file_output=None, summary={},
            error_message='audit_toolkit module not found. Install pandas, openpyxl, numpy.'
        )
    
    try:
        import pandas as pd
        
        path = Path(filepath)
        if output_dir is None:
            output_dir = path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        stem = path.stem
        
        # Process
        processor = audit_toolkit.ExcelAuditProcessorV2()
        df = processor.read_excel_multiheader(filepath, header_rows=[0, 1])
        
        if df is None:
            return AuditResult(
                jenis='keuangan', status='error', file_input=filepath,
                file_output=None, summary={},
                error_message='Failed to read Excel file'
            )
        
        processor.detect_and_convert_numbers(df)
        processor.calculate_financial_ratios(df)
        
        # Anomaly detection
        anomalies = processor.detect_anomalies(df, method='all')
        
        # Analysis
        analyzer = audit_toolkit.BUMDAnalyzer(df)
        low_roa = analyzer.filter_by_roa(max_roa=5)
        underperforming = analyzer.get_underperforming()
        
        # Export
        output_file = output_dir / f"hasil_audit_keuangan_{stem}.xlsx"
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data_Lengkap', index=False)
            if len(low_roa) > 0:
                low_roa.to_excel(writer, sheet_name='ROA_Rendah', index=False)
            if len(underperforming) > 0:
                underperforming.to_excel(writer, sheet_name='Underperforming', index=False)
            
            # Summary sheet
            summary = pd.DataFrame({
                'Kategori': ['Total BUMD', 'ROA < 5%', 'Underperforming', 'Normal', 'Anomaly Flags'],
                'Jumlah': [
                    len(df), len(low_roa), len(underperforming),
                    len(df) - len(underperforming),
                    sum(len(v) for v in anomalies.values())
                ]
            })
            summary.to_excel(writer, sheet_name='Ringkasan', index=False)
            
            # Anomalies sheet
            if anomalies:
                anomaly_rows = []
                for col, flags in anomalies.items():
                    for flag in flags:
                        anomaly_rows.append({
                            'Kolom': col,
                            'Metode': flag['method'],
                            'Jumlah': flag['count'],
                            'Deskripsi': flag['description']
                        })
                pd.DataFrame(anomaly_rows).to_excel(writer, sheet_name='Anomali', index=False)
        
        return AuditResult(
            jenis='keuangan', status='success', file_input=filepath,
            file_output=str(output_file),
            summary={
                'total_bumd': len(df),
                'roa_rendah': len(low_roa),
                'underperforming': len(underperforming),
                'anomaly_flags': sum(len(v) for v in anomalies.values()),
                'anomaly_details': anomalies,
                'columns': len(df.columns),
                'rows': len(df)
            }
        )
        
    except Exception as e:
        return AuditResult(
            jenis='keuangan', status='error', file_input=filepath,
            file_output=None, summary={},
            error_message=str(e)
        )


def run_audit_spi(filepath: str, nama_entitas: str = "Entitas Audit",
                  output_dir: Optional[str] = None) -> AuditResult:
    """Run SPI audit from Excel input.
    
    Args:
        filepath: Path to Excel with columns: komponen, indikator, nilai, keterangan
        nama_entitas: Name of entity being audited
        output_dir: Directory to save output
    
    Returns:
        AuditResult with SPI scores and recommendations
    """
    template = _safe_import('template_audit_spi')
    if template is None:
        return AuditResult(
            jenis='spi', status='error', file_input=filepath,
            file_output=None, summary={},
            error_message='template_audit_spi module not found'
        )
    
    try:
        path = Path(filepath)
        if output_dir is None:
            output_dir = path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        stem = path.stem
        
        audit = template.AuditSPI(nama_entitas=nama_entitas)
        success = audit.input_from_excel(filepath)
        
        if not success:
            return AuditResult(
                jenis='spi', status='error', file_input=filepath,
                file_output=None, summary={},
                error_message='Failed to read SPI data from Excel. Required columns: komponen, indikator, nilai'
            )
        
        hasil = audit.hitung_nilai_spi()
        
        if hasil is None:
            return AuditResult(
                jenis='spi', status='error', file_input=filepath,
                file_output=None, summary={},
                error_message='SPI calculation returned no results'
            )
        
        output_file = output_dir / f"hasil_audit_spi_{stem}.xlsx"
        audit.generate_laporan(str(output_file))
        
        # Build summary
        komponen_summary = {}
        for kode, data in hasil['komponen'].items():
            komponen_summary[kode] = {
                'nama': data['nama'],
                'nilai': round(data['rata_rata'], 2),
                'bobot': data['bobot'],
                'nilai_bobot': round(data['nilai_bobot'], 2)
            }
        
        return AuditResult(
            jenis='spi', status='success', file_input=filepath,
            file_output=str(output_file),
            summary={
                'nama_entitas': nama_entitas,
                'nilai_total': round(hasil['nilai_total'], 2),
                'kategori': hasil['kategori']['tingkat'],
                'deskripsi': hasil['kategori']['deskripsi'],
                'komponen': komponen_summary,
                'rekomendasi_count': len(hasil['rekomendasi']),
                'rekomendasi': hasil['rekomendasi'][:5]  # Top 5
            }
        )
        
    except Exception as e:
        return AuditResult(
            jenis='spi', status='error', file_input=filepath,
            file_output=None, summary={},
            error_message=str(e)
        )


def run_audit_kinerja(filepath: str, tahun: int = 2024,
                      output_dir: Optional[str] = None) -> AuditResult:
    """Run performance audit from Excel input.
    
    Args:
        filepath: Path to Excel with performance indicator columns
        tahun: Year being audited
        output_dir: Directory to save output
    
    Returns:
        AuditResult with rankings and scores
    """
    template = _safe_import('template_audit_kinerja')
    if template is None:
        return AuditResult(
            jenis='kinerja', status='error', file_input=filepath,
            file_output=None, summary={},
            error_message='template_audit_kinerja module not found'
        )
    
    try:
        path = Path(filepath)
        if output_dir is None:
            output_dir = path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        stem = path.stem
        
        audit = template.AuditKinerja(tahun=tahun)
        success = audit.load_data(filepath)
        
        if not success:
            return AuditResult(
                jenis='kinerja', status='error', file_input=filepath,
                file_output=None, summary={},
                error_message='Failed to load performance data'
            )
        
        hasil = audit.hitung_skor()
        
        if hasil is None:
            return AuditResult(
                jenis='kinerja', status='error', file_input=filepath,
                file_output=None, summary={},
                error_message='Performance scoring returned no results'
            )
        
        output_file = output_dir / f"hasil_audit_kinerja_{stem}.xlsx"
        audit.generate_laporan(str(output_file))
        
        # Categorize
        predikat_count = {}
        for h in hasil:
            p = h['kategori']['predikat']
            predikat_count[p] = predikat_count.get(p, 0) + 1
        
        top5 = [
            {'ranking': h['ranking'], 'nama': h['nama'], 'skor': round(h['skor_total'], 2), 'predikat': h['kategori']['predikat']}
            for h in hasil[:5]
        ]
        bottom5 = [
            {'ranking': h['ranking'], 'nama': h['nama'], 'skor': round(h['skor_total'], 2), 'predikat': h['kategori']['predikat']}
            for h in hasil[-5:]
        ]
        
        return AuditResult(
            jenis='kinerja', status='success', file_input=filepath,
            file_output=str(output_file),
            summary={
                'tahun': tahun,
                'total_entitas': len(hasil),
                'skor_tertinggi': round(hasil[0]['skor_total'], 2),
                'skor_terendah': round(hasil[-1]['skor_total'], 2),
                'predikat_distribution': predikat_count,
                'top_5': top5,
                'bottom_5': bottom5
            }
        )
        
    except Exception as e:
        return AuditResult(
            jenis='kinerja', status='error', file_input=filepath,
            file_output=None, summary={},
            error_message=str(e)
        )


def list_templates() -> List[Dict]:
    """Return list of available audit templates with descriptions."""
    return [
        {
            'id': 'keuangan',
            'nama': 'Audit Keuangan',
            'icon': '🔢',
            'deskripsi': 'Analisis rasio keuangan (ROA, ROE, DER), deteksi anomali, filter BUMD bermasalah',
            'input_format': 'Excel multi-header dengan kolom: aset, kewajiban, ekuitas, laba, pendapatan',
            'output': 'Excel + PDF + Grafik'
        },
        {
            'id': 'spi',
            'nama': 'Audit SPI',
            'icon': '🛡️',
            'deskripsi': 'Evaluasi Sistem Pengendalian Intern berbasis COSO Framework (5 komponen)',
            'input_format': 'Excel dengan kolom: komponen, indikator, nilai (1-5), keterangan',
            'output': 'Excel dengan rekomendasi perbaikan'
        },
        {
            'id': 'kinerja',
            'nama': 'Audit Kinerja',
            'icon': '📊',
            'deskripsi': 'Scoring kinerja entitas dengan ranking A/B/C/D/E, top/bottom performer',
            'input_format': 'Excel dengan kolom indikator kinerja (realisasi_anggaran, efisiensi_biaya, dll)',
            'output': 'Excel + Visualisasi'
        }
    ]


def _chart_cache_key(result: AuditResult) -> str:
    from src.utils.cache import _make_key
    summary_json = json.dumps(result.summary, sort_keys=True, default=str)
    return _make_key("generate_chart_data", (result.jenis,), {"summary_hash": hashlib.md5(summary_json.encode()).hexdigest()})


@ttl_cache(ttl_seconds=300, key_func=lambda result: _chart_cache_key(result))
def generate_chart_data(result: AuditResult) -> Dict[str, Any]:
    """Generate Chart.js compatible data from audit result.
    
    Returns:
        Dict with chart configurations for each audit type.
    """
    charts = {}
    
    if result.status != 'success' or not result.summary:
        return charts
    
    s = result.summary
    
    if result.jenis == 'keuangan':
        # Chart 1: Financial Health Distribution (Pie)
        charts['health_pie'] = {
            'type': 'doughnut',
            'title': 'Distribusi Kesehatan Keuangan',
            'data': {
                'labels': ['Normal', 'ROA Rendah', 'Underperforming'],
                'datasets': [{
                    'data': [
                        max(0, s.get('total_bumd', 0) - s.get('underperforming', 0)),
                        s.get('roa_rendah', 0),
                        s.get('underperforming', 0)
                    ],
                    'backgroundColor': ['#22c55e', '#eab308', '#ef4444']
                }]
            }
        }
        
        # Chart 2: Anomaly Flags (Bar)
        anomaly_details = s.get('anomaly_details', {})
        if anomaly_details:
            labels = list(anomaly_details.keys())
            values = [sum(1 for f in flags if f.get('count') not in (0, 'N/A')) or len(flags) for flags in anomaly_details.values()]
            charts['anomaly_bar'] = {
                'type': 'bar',
                'title': 'Anomaly Flags per Kolom',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Flags',
                        'data': values,
                        'backgroundColor': '#f97316'
                    }]
                }
            }
    
    elif result.jenis == 'spi':
        # Chart 1: SPI Component Scores (Radar)
        komponen = s.get('komponen', {})
        if komponen:
            labels = [v['nama'] for v in komponen.values()]
            values = [v['nilai'] for v in komponen.values()]
            charts['spi_radar'] = {
                'type': 'radar',
                'title': 'Penilaian SPI per Komponen',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Nilai',
                        'data': values,
                        'backgroundColor': 'rgba(6, 182, 212, 0.2)',
                        'borderColor': '#06b6d4',
                        'pointBackgroundColor': '#06b6d4'
                    }]
                },
                'options': {
                    'scales': {'r': {'min': 0, 'max': 5}}
                }
            }
        
        # Chart 2: SPI Category Gauge (Bar horizontal)
        kategori = s.get('kategori', 'N/A')
        category_scores = {'SANGAT BAIK': 5, 'BAIK': 4, 'CUKUP': 3, 'LEMAH': 2, 'SANGAT LEMAH': 1}
        score = category_scores.get(kategori, 3)
        charts['spi_gauge'] = {
            'type': 'bar',
            'title': f'Nilai SPI: {s.get("nilai_total", 0):.2f} / 5.00 ({kategori})',
            'data': {
                'labels': ['SPI Score'],
                'datasets': [{
                    'label': 'Nilai',
                    'data': [score],
                    'backgroundColor': '#22c55e' if score >= 4 else '#eab308' if score >= 3 else '#ef4444'
                }]
            },
            'options': {
                'indexAxis': 'y',
                'scales': {'x': {'min': 0, 'max': 5}}
            }
        }
    
    elif result.jenis == 'kinerja':
        # Chart 1: Predikat Distribution (Pie)
        predikat = s.get('predikat_distribution', {})
        if predikat:
            labels = sorted(predikat.keys())
            values = [predikat[p] for p in labels]
            color_map = {'A': '#22c55e', 'B': '#4ade80', 'C': '#eab308', 'D': '#f97316', 'E': '#ef4444'}
            charts['predikat_pie'] = {
                'type': 'doughnut',
                'title': 'Distribusi Predikat Kinerja',
                'data': {
                    'labels': [f'Predikat {p}' for p in labels],
                    'datasets': [{
                        'data': values,
                        'backgroundColor': [color_map.get(p, '#94a3b8') for p in labels]
                    }]
                }
            }
        
        # Chart 2: Top vs Bottom Performers (Bar)
        top5 = s.get('top_5', [])
        bottom5 = s.get('bottom_5', [])
        if top5 or bottom5:
            charts['ranking_bar'] = {
                'type': 'bar',
                'title': 'Top 5 & Bottom 5 Performer',
                'data': {
                    'labels': [p['nama'][:20] for p in top5] + [p['nama'][:20] for p in bottom5],
                    'datasets': [{
                        'label': 'Skor',
                        'data': [p['skor'] for p in top5] + [p['skor'] for p in bottom5],
                        'backgroundColor': ['#22c55e'] * len(top5) + ['#ef4444'] * len(bottom5)
                    }]
                }
            }
        
        # Chart 3: Score Distribution (Histogram-style Bar)
        # Use bins: 0-60, 60-70, 70-80, 80-90, 90-100
        total = s.get('total_entitas', 0)
        if total > 0:
            # Approximate from predikat distribution
            dist = {'0-60 (E)': predikat.get('E', 0), '60-70 (D)': predikat.get('D', 0),
                    '70-80 (C)': predikat.get('C', 0), '80-90 (B)': predikat.get('B', 0),
                    '90-100 (A)': predikat.get('A', 0)}
            charts['score_dist'] = {
                'type': 'bar',
                'title': 'Distribusi Skor Kinerja',
                'data': {
                    'labels': list(dist.keys()),
                    'datasets': [{
                        'label': 'Jumlah Entitas',
                        'data': list(dist.values()),
                        'backgroundColor': ['#ef4444', '#f97316', '#eab308', '#4ade80', '#22c55e']
                    }]
                }
            }
    
    return charts


def run_batch_audit(jenis: str, filenames: List[str], **kwargs) -> Dict:
    """Run audit on multiple files sequentially.
    
    Args:
        jenis: 'keuangan', 'spi', or 'kinerja'
        filenames: List of filenames in data/uploads/
        **kwargs: Additional args passed to specific audit runner
    
    Returns:
        Dict with combined summary and individual results
    """
    results = []
    for filename in filenames:
        upload_dir = BASE_DIR / "data" / "uploads"
        filepath = str(upload_dir / filename)
        result = run_audit(jenis, filepath, **kwargs)
        results.append({"filename": filename, **result})
    
    successful = sum(1 for r in results if r.get("status") == "success")
    failed = sum(1 for r in results if r.get("status") == "error")
    
    return {
        "status": "success" if successful > 0 else "error",
        "jenis": jenis,
        "total_files": len(filenames),
        "successful": successful,
        "failed": failed,
        "results": results,
    }


def run_audit(jenis: str, filepath: str, **kwargs) -> Dict:
    """Unified entry point to run any audit type.
    
    Args:
        jenis: 'keuangan', 'spi', atau 'kinerja'
        filepath: Path to input Excel file
        **kwargs: Additional args passed to specific audit runner
    
    Returns:
        Dict representation of AuditResult with chart data included
    """
    runners = {
        'keuangan': run_audit_keuangan,
        'spi': run_audit_spi,
        'kinerja': run_audit_kinerja
    }
    
    if jenis not in runners:
        error_result = asdict(AuditResult(
            jenis=jenis, status='error', file_input=filepath,
            file_output=None, summary={},
            error_message=f"Jenis audit '{jenis}' tidak tersedia. Pilih: keuangan, spi, kinerja"
        ))
        log_audit_run(
            jenis=jenis, filename=Path(filepath).name,
            status='error', summary={'error': error_result.get('error_message')}
        )
        return error_result
    
    start = time.time()
    result = runners[jenis](filepath, **kwargs)
    duration_ms = int((time.time() - start) * 1000)
    result_dict = asdict(result)
    
    # Generate chart data and attach to result
    try:
        chart_data = generate_chart_data(result)
        result_dict['charts'] = chart_data
    except Exception:
        result_dict['charts'] = {}
    
    # Log to audit trail
    try:
        log_audit_run(
            jenis=result.jenis,
            filename=Path(filepath).name,
            status=result.status,
            output_path=result.file_output,
            summary=result.summary,
            charts=result_dict.get('charts'),
            duration_ms=duration_ms,
        )
    except Exception:
        pass  # Never fail audit because of logging
    
    return result_dict
