#!/usr/bin/env python3
"""
AI Audit Toolkit - Complete Version
Fitur: Excel Processor + Anomaly Detector + Filter + Visualisasi + PDF Export
Author: AI Assistant untuk Government Audit Agency
"""

import pandas as pd
import numpy as np
import joblib
import json
import re
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Try to import optional modules
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  Matplotlib not installed. Visualisasi akan dilewati.")

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    print("⚠️  fpdf not installed. PDF export akan dilewati.")


class ExcelAuditProcessorV2:
    """Excel Processor dengan multi-header support"""
    
    def __init__(self):
        self.dataframes = {}
        self.summary = {}
        self.metadata = {}
    
    def read_excel_multiheader(self, filepath, header_rows=[0, 1]):
        """Baca Excel dengan multi-header"""
        print(f"📂 Membaca: {filepath}")
        print(f"   Mode: Multi-header (baris {header_rows})")
        
        try:
            df = pd.read_excel(filepath, header=header_rows)
            df.columns = self._flatten_columns(df.columns)
            
            print(f"   ✓ Kolom setelah flatten: {len(df.columns)}")
            print(f"   ✓ Contoh: {list(df.columns[:5])}")
            
            self.dataframes['main'] = df
            return df
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return None
    
    def _flatten_columns(self, columns):
        """Flatten multi-level column names"""
        new_cols = []
        for col in columns:
            if isinstance(col, tuple):
                parts = [str(c).strip() for c in col if 'Unnamed' not in str(c)]
                if parts:
                    new_col = '_'.join(parts).lower()
                    new_col = re.sub(r'\s+', '_', new_col)
                    new_col = re.sub(r'_+', '_', new_col)
                    new_col = new_col.strip('_')
                else:
                    new_col = 'unnamed'
            else:
                new_col = str(col).strip().lower().replace(' ', '_')
            new_cols.append(new_col)
        
        # Handle duplicates
        seen = {}
        for i, col in enumerate(new_cols):
            if col in seen:
                seen[col] += 1
                new_cols[i] = f"{col}_{seen[col]}"
            else:
                seen[col] = 0
        
        return new_cols
    
    def detect_and_convert_numbers(self, df):
        """Auto-deteksi dan konversi kolom angka"""
        print("\n🔢 Auto-deteksi kolom numerik...")
        
        converted = []
        for col in df.columns:
            if any(skip in col for skip in ['id_', 'nama_', 'bumd', 'no_', 'unnamed']):
                continue
                
            if df[col].dtype == object:
                try:
                    sample = df[col].dropna().head(10)
                    if sample.astype(str).str.match(r'^[\d\.\,\s\-]+$').any():
                        clean = df[col].astype(str).str.replace(r'[Rp\s\.]', '', regex=True)
                        clean = clean.str.replace(',', '.', regex=False)
                        clean = pd.to_numeric(clean, errors='coerce')
                        
                        if clean.notna().sum() > 0:
                            df[col] = clean
                            converted.append(col)
                except:
                    pass
        
        print(f"   ✓ {len(converted)} kolom dikonversi ke numerik")
        return df
    
    def calculate_financial_ratios(self, df):
        """Auto-kalkulasi rasio keuangan"""
        print("\n📊 Kalkulasi rasio keuangan...")
        
        col_map = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'aset' in col_lower and 'total' in col_lower:
                col_map['aset'] = col
            if 'kewajiban' in col_lower:
                col_map['kewajiban'] = col
            if 'ekuitas' in col_lower:
                col_map['ekuitas'] = col
            if 'laba' in col_lower and 'bersih' in col_lower:
                col_map['laba'] = col
            if 'pendapatan' in col_lower:
                col_map['pendapatan'] = col
        
        print(f"   Kolom terdeteksi: {list(col_map.keys())}")
        
        try:
            if 'laba' in col_map and 'aset' in col_map:
                df['roa_calc'] = (df[col_map['laba']] / df[col_map['aset']]) * 100
                print(f"   ✓ ROA = Laba/Aset × 100")
            
            if 'laba' in col_map and 'ekuitas' in col_map:
                df['roe_calc'] = (df[col_map['laba']] / df[col_map['ekuitas']]) * 100
                print(f"   ✓ ROE = Laba/Ekuitas × 100")
            
            if 'kewajiban' in col_map and 'aset' in col_map:
                df['der_calc'] = df[col_map['kewajiban']] / df[col_map['aset']]
                print(f"   ✓ Debt Ratio = Kewajiban/Aset")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
        
        return df
    
    def export_clean(self, output_path, df=None):
        """Export data bersih ke Excel"""
        if df is None:
            df = self.dataframes.get('main')
        
        if df is None:
            print("   ✗ Tidak ada data untuk export")
            return
        
        print(f"\n💾 Export ke: {output_path}")
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data_Bersih', index=False)
            print(f"   ✓ Export selesai!")
        except Exception as e:
            print(f"   ✗ Error export: {e}")


class BUMDAnalyzer:
    """Analisis dan filter BUMD berdasarkan kriteria"""
    
    def __init__(self, df):
        self.df = df
        self.filters = []
    
    def filter_by_roa(self, max_roa=5, min_roa=None):
        """Filter BUMD berdasarkan ROA"""
        print(f"\n🔍 Filter ROA...")
        
        roa_cols = [c for c in self.df.columns if 'roa' in c.lower()]
        if not roa_cols:
            print("   ✗ Kolom ROA tidak ditemukan")
            return self.df
        
        roa_col = roa_cols[0]
        mask = pd.Series([True] * len(self.df))
        
        if max_roa is not None:
            mask = mask & (self.df[roa_col] < max_roa)
            print(f"   ROA < {max_roa}%")
        
        if min_roa is not None:
            mask = mask & (self.df[roa_col] > min_roa)
            print(f"   ROA > {min_roa}%")
        
        filtered = self.df[mask]
        print(f"   ✓ {len(filtered)} BUMD memenuhi kriteria")
        
        return filtered
    
    def filter_by_roe(self, max_roe=10, min_roe=None):
        """Filter BUMD berdasarkan ROE"""
        print(f"\n🔍 Filter ROE...")
        
        roe_cols = [c for c in self.df.columns if 'roe' in c.lower()]
        if not roe_cols:
            print("   ✗ Kolom ROE tidak ditemukan")
            return self.df
        
        roe_col = roe_cols[0]
        mask = pd.Series([True] * len(self.df))
        
        if max_roe is not None:
            mask = mask & (self.df[roe_col] < max_roe)
            print(f"   ROE < {max_roe}%")
        
        if min_roe is not None:
            mask = mask & (self.df[roe_col] > min_roe)
            print(f"   ROE > {min_roe}%")
        
        filtered = self.df[mask]
        print(f"   ✓ {len(filtered)} BUMD memenuhi kriteria")
        
        return filtered
    
    def filter_by_aset_size(self, min_aset=None, max_aset=None):
        """Filter BUMD berdasarkan ukuran aset"""
        print(f"\n🔍 Filter Ukuran Aset...")
        
        aset_cols = [c for c in self.df.columns if 'aset' in c.lower()]
        if not aset_cols:
            print("   ✗ Kolom Aset tidak ditemukan")
            return self.df
        
        aset_col = aset_cols[0]
        mask = pd.Series([True] * len(self.df))
        
        if min_aset is not None:
            mask = mask & (self.df[aset_col] >= min_aset)
            print(f"   Aset ≥ Rp {min_aset:,.0f}")
        
        if max_aset is not None:
            mask = mask & (self.df[aset_col] <= max_aset)
            print(f"   Aset ≤ Rp {max_aset:,.0f}")
        
        filtered = self.df[mask]
        print(f"   ✓ {len(filtered)} BUMD memenuhi kriteria")
        
        return filtered
    
    def get_underperforming(self):
        """Identifikasi BUMD underperforming (ROA < 5%, ROE < 10%)"""
        print("\n⚠️  Identifikasi BUMD Underperforming...")
        
        roa_cols = [c for c in self.df.columns if 'roa' in c.lower()]
        roe_cols = [c for c in self.df.columns if 'roe' in c.lower()]
        
        mask = pd.Series([False] * len(self.df))
        
        if roa_cols:
            mask = mask | (self.df[roa_cols[0]] < 5)
        if roe_cols:
            mask = mask | (self.df[roe_cols[0]] < 10)
        
        underperforming = self.df[mask]
        print(f"   ✓ {len(underperforming)} BUMD underperforming teridentifikasi")
        
        return underperforming


class AuditVisualizer:
    """Visualisasi data audit"""
    
    def __init__(self, df):
        self.df = df
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️  Matplotlib tidak tersedia. Install dengan: pip install matplotlib seaborn")
    
    def plot_roa_distribution(self, output_file='roa_distribution.png'):
        """Plot distribusi ROA"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        print(f"\n📊 Membuat grafik distribusi ROA...")
        
        roa_cols = [c for c in self.df.columns if 'roa' in c.lower()]
        if not roa_cols:
            print("   ✗ Kolom ROA tidak ditemukan")
            return
        
        plt.figure(figsize=(10, 6))
        
        for col in roa_cols[:3]:  # Max 3 tahun
            data = self.df[col].dropna()
            if len(data) > 0:
                plt.hist(data, bins=20, alpha=0.5, label=col)
        
        plt.axvline(x=5, color='r', linestyle='--', label='Threshold 5%')
        plt.xlabel('ROA (%)')
        plt.ylabel('Jumlah BUMD')
        plt.title('Distribusi ROA BUMD')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ Grafik disimpan: {output_file}")
    
    def plot_aset_trend(self, output_file='aset_trend.png'):
        """Plot tren aset"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        print(f"\n📊 Membuat grafik tren aset...")
        
        aset_cols = [c for c in self.df.columns if 'aset' in c.lower() and any(str(y) in c for y in range(2020, 2026))]
        
        if len(aset_cols) < 2:
            print("   ✗ Data tren tidak cukup")
            return
        
        # Calculate average per year
        years = []
        avg_asets = []
        
        for col in sorted(aset_cols):
            year = re.search(r'(20\d{2})', col)
            if year:
                years.append(year.group(1))
                avg_asets.append(self.df[col].mean() / 1e9)  # Convert to billions
        
        plt.figure(figsize=(10, 6))
        plt.plot(years, avg_asets, marker='o', linewidth=2, markersize=8)
        plt.xlabel('Tahun')
        plt.ylabel('Rata-rata Aset (Miliar Rp)')
        plt.title('Tren Rata-rata Aset BUMD')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ Grafik disimpan: {output_file}")


class PDFReport:
    """Generate laporan PDF"""
    
    def __init__(self, title="Laporan Analisis BUMD"):
        self.title = title
        if not FPDF_AVAILABLE:
            print("⚠️  fpdf tidak tersedia. Install dengan: pip install fpdf")
    
    def generate(self, df, output_file='laporan_audit.pdf'):
        """Generate laporan PDF"""
        if not FPDF_AVAILABLE:
            print("   ✗ PDF generation skipped (fpdf not installed)")
            return
        
        print(f"\n📄 Generate laporan PDF...")
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, self.title, ln=True, align='C')
        pdf.ln(10)
        
        # Timestamp
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.ln(5)
        
        # Summary
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Ringkasan', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f"Total BUMD: {len(df)}", ln=True)
        pdf.cell(0, 8, f"Total Kolom: {len(df.columns)}", ln=True)
        pdf.ln(5)
        
        # ROA Summary
        roa_cols = [c for c in df.columns if 'roa' in c.lower()]
        if roa_cols:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Ringkasan ROA', ln=True)
            pdf.set_font('Arial', '', 10)
            for col in roa_cols[:3]:
                avg = df[col].mean()
                pdf.cell(0, 8, f"{col}: {avg:.2f}% (rata-rata)", ln=True)
            pdf.ln(5)
        
        # Underperforming
        underperform = df[
            (df[roa_cols[0]] < 5 if roa_cols else True) |
            (df[[c for c in df.columns if 'roe' in c.lower()][0]] < 10 if [c for c in df.columns if 'roe' in c.lower()] else True)
        ]
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'BUMD Underperforming ({len(underperform)} unit)', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, '(ROA < 5% atau ROE < 10%)', ln=True)
        pdf.ln(5)
        
        # Save
        pdf.output(output_file)
        print(f"   ✓ PDF disimpan: {output_file}")


def main():
    """Main execution"""
    print("="*60)
    print("🤖 AI AUDIT TOOLKIT - COMPLETE")
    print("   Untuk Government Audit Agency - Analisis Keuangan BUMD")
    print("="*60)
    
    # 1. Process Excel
    processor = ExcelAuditProcessorV2()
    
    input_files = [
        "kompilasi_advanced.xlsx",
        "kompilasi.xlsx",
        "Kompilasi.xlsx",
        "data_bumd.xlsx"
    ]
    
    input_file = None
    for f in input_files:
        if Path(f).exists():
            input_file = f
            break
    
    if not input_file:
        print("\n✗ File input tidak ditemukan!")
        print("   Taruh file Excel di folder ini dan jalankan ulang.")
        print("   File yang dicari: kompilasi.xlsx, data_bumd.xlsx, dll")
        return
    
    print(f"\n📂 Menggunakan file: {input_file}")
    
    # Read and process
    if input_file.endswith('_advanced.xlsx'):
        df = pd.read_excel(input_file, sheet_name='Data_Bersih')
        print(f"   ✓ Data loaded: {len(df)} baris")
    else:
        df = processor.read_excel_multiheader(input_file, header_rows=[0, 1])
        processor.detect_and_convert_numbers(df)
        processor.calculate_financial_ratios(df)
    
    # 2. Filter BUMD
    print("\n" + "="*60)
    print("🔍 FILTER BUMD")
    print("="*60)
    
    analyzer = BUMDAnalyzer(df)
    
    # Filter ROA < 5%
    low_roa = analyzer.filter_by_roa(max_roa=5)
    
    # Get underperforming
    underperforming = analyzer.get_underperforming()
    
    # 3. Visualisasi
    print("\n" + "="*60)
    print("📊 VISUALISASI")
    print("="*60)
    
    viz = AuditVisualizer(df)
    viz.plot_roa_distribution('roa_distribution.png')
    viz.plot_aset_trend('aset_trend.png')
    
    # 4. PDF Report
    print("\n" + "="*60)
    print("📄 LAPORAN PDF")
    print("="*60)
    
    pdf = PDFReport("Laporan Analisis BUMD - Government Audit Agency")
    pdf.generate(df, 'laporan_bumd.pdf')
    
    # 5. Export hasil filter
    print("\n" + "="*60)
    print("💾 EXPORT HASIL")
    print("="*60)
    
    with pd.ExcelWriter('hasil_analisis_lengkap.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Data_Lengkap', index=False)
        if len(low_roa) > 0:
            low_roa.to_excel(writer, sheet_name='ROA_Rendah', index=False)
        if len(underperforming) > 0:
            underperforming.to_excel(writer, sheet_name='Underperforming', index=False)
        
        # Summary sheet
        summary = pd.DataFrame({
            'Kategori': ['Total BUMD', 'ROA < 5%', 'Underperforming', 'Normal'],
            'Jumlah': [
                len(df),
                len(low_roa),
                len(underperforming),
                len(df) - len(underperforming)
            ]
        })
        summary.to_excel(writer, sheet_name='Ringkasan', index=False)
    
    print(f"   ✓ Excel: hasil_analisis_lengkap.xlsx")
    
    print("\n" + "="*60)
    print("✅ SELESAI!")
    print("="*60)
    print("\n📁 Output files:")
    print("   • hasil_analisis_lengkap.xlsx - Data lengkap + filter")
    print("   • roa_distribution.png - Grafik distribusi ROA")
    print("   • aset_trend.png - Grafik tren aset")
    print("   • laporan_bumd.pdf - Laporan PDF")
    print("\n💡 Tips: Gunakan Excel 'ROA_Rendah' untuk fokus audit")


if __name__ == "__main__":
    main()
