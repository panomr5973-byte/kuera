#!/usr/bin/env python3
"""
Template Master - Menu Utama AI Audit Toolkit
Integrasi semua jenis audit
"""

import sys
import os
from pathlib import Path


def print_banner():
    """Print banner aplikasi"""
    print("="*70)
    print("  🤖 AI AUDIT TOOLKIT - Government Audit Agency")
    print("  Sistem Pendukung Audit untuk Government Audit Agency")
    print("="*70)
    print()


def print_menu():
    """Print menu utama"""
    print("PILIH JENIS AUDIT:")
    print("-"*70)
    print("1. 🔢 AUDIT KEUANGAN (BUMD/Entitas)")
    print("   - Analisis rasio keuangan (ROA, ROE, DER)")
    print("   - Deteksi anomali otomatis")
    print("   - Filter BUMD bermasalah")
    print("   - Output: Excel + Grafik + PDF")
    print()
    print("2. 🛡️  AUDIT SPI (Sistem Pengendalian Intern)")
    print("   - Evaluasi COSO Framework")
    print("   - Penilaian 5 komponen SPI")
    print("   - Rekomendasi perbaikan")
    print("   - Output: Excel dengan rekomendasi")
    print()
    print("3. 📊 AUDIT KINERJA")
    print("   - Scoring kinerja entitas")
    print("   - Ranking A/B/C/D/E")
    print("   - Top/Bottom performer")
    print("   - Output: Excel + Visualisasi")
    print()
    print("4. 📝 LIHAT CONTOH KODE")
    print("   - Contoh penggunaan setiap template")
    print()
    print("5. ❌ KELUAR")
    print("-"*70)


def run_audit_keuangan():
    """Jalankan audit keuangan"""
    print("\n" + "="*70)
    print("AUDIT KEUANGAN")
    print("="*70)
    
    try:
        from audit_toolkit import (
            ExcelAuditProcessorV2, 
            BUMDAnalyzer, 
            AuditVisualizer,
            PDFReport
        )
        import pandas as pd
        from pathlib import Path
        
        print("\n📂 Cari file input...")
        input_files = [
            "kompilasi.xlsx",
            "Kompilasi.xlsx",
            "data_bumd.xlsx",
            "data_keuangan.xlsx"
        ]
        
        input_file = None
        for f in input_files:
            if Path(f).exists():
                input_file = f
                break
        
        if not input_file:
            print("\n✗ File tidak ditemukan!")
            print("   Pastikan ada file Excel (kompilasi.xlsx, data_bumd.xlsx, dll)")
            print("   di folder yang sama dengan script ini.")
            return
        
        print(f"   ✓ Menggunakan: {input_file}")
        
        # Proses
        processor = ExcelAuditProcessorV2()
        df = processor.read_excel_multiheader(input_file, header_rows=[0, 1])
        
        if df is None:
            print("   ✗ Gagal membaca file")
            return
        
        processor.detect_and_convert_numbers(df)
        processor.calculate_financial_ratios(df)
        
        # Analisis
        print("\n" + "-"*70)
        print("ANALISIS")
        print("-"*70)
        
        analyzer = BUMDAnalyzer(df)
        low_roa = analyzer.filter_by_roa(max_roa=5)
        underperforming = analyzer.get_underperforming()
        
        # Export
        print("\n" + "-"*70)
        print("EXPORT HASIL")
        print("-"*70)
        
        with pd.ExcelWriter('hasil_audit_keuangan.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data_Lengkap', index=False)
            if len(low_roa) > 0:
                low_roa.to_excel(writer, sheet_name='ROA_Rendah', index=False)
            if len(underperforming) > 0:
                underperforming.to_excel(writer, sheet_name='Underperforming', index=False)
        
        print("   ✓ Excel: hasil_audit_keuangan.xlsx")
        
        # Visualisasi
        viz = AuditVisualizer(df)
        viz.plot_roa_distribution('roa_dist.png')
        viz.plot_aset_trend('aset_trend.png')
        
        # PDF
        pdf = PDFReport("Laporan Audit Keuangan")
        pdf.generate(df, 'laporan_keuangan.pdf')
        
        print("\n✅ Audit keuangan selesai!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("   Pastikan semua library terinstall:")
        print("   pip install pandas numpy matplotlib openpyxl fpdf")


def run_audit_spi():
    """Jalankan audit SPI"""
    print("\n" + "="*70)
    print("AUDIT SPI")
    print("="*70)
    
    try:
        from template_audit_spi import AuditSPI
        
        print("\n📂 Cari file penilaian SPI...")
        
        if Path("data_spi.xlsx").exists():
            print("   ✓ Menggunakan: data_spi.xlsx")
            audit = AuditSPI(nama_entitas="Entitas Audit")
            audit.input_from_excel("data_spi.xlsx")
            audit.hitung_nilai_spi()
            audit.print_ringkasan()
            audit.generate_laporan('hasil_audit_spi.xlsx')
            print("\n✅ Audit SPI selesai!")
        else:
            print("\n⚠️  File data_spi.xlsx tidak ditemukan")
            print("\nContoh format file data_spi.xlsx:")
            print("-"*70)
            print("| komponen              | indikator              | nilai | keterangan |")
            print("-"*70)
            print("| LINGKUNGAN_PENGENDALIAN | Integritas dan Nilai   | 4     | Sudah baik |")
            print("| PENILAIAN_RISIKO      | Identifikasi Risiko    | 2     | Perlu perbaikan |")
            print("-"*70)
            print("\nKomponen yang tersedia:")
            spi = AuditSPI()
            for kode, info in spi.komponen_spi.items():
                print(f"   • {kode}: {info['nama']}")
            
            print("\nAtau jalankan demo:")
            print("   python template_audit_spi.py demo")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")


def run_audit_kinerja():
    """Jalankan audit kinerja"""
    print("\n" + "="*70)
    print("AUDIT KINERJA")
    print("="*70)
    
    try:
        from template_audit_kinerja import AuditKinerja
        
        print("\n📂 Cari file data kinerja...")
        
        input_files = ["data_kinerja.xlsx", "kinerja.xlsx", "data_kinerja_sample.xlsx"]
        input_file = None
        
        for f in input_files:
            if Path(f).exists():
                input_file = f
                break
        
        if input_file:
            print(f"   ✓ Menggunakan: {input_file}")
            audit = AuditKinerja(tahun=2024)
            audit.load_data(input_file)
            audit.hitung_skor()
            audit.print_ringkasan()
            audit.generate_laporan('hasil_audit_kinerja.xlsx')
            audit.visualisasi('kinerja')
            print("\n✅ Audit kinerja selesai!")
        else:
            print("\n⚠️  File tidak ditemukan")
            print("\nJalankan demo terlebih dahulu:")
            print("   python template_audit_kinerja.py demo")
            print("\nAtau siapkan file Excel dengan kolom:")
            print("   nama, realisasi_anggaran, efisiensi_biaya, dsb.")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")


def show_examples():
    """Tampilkan contoh kode"""
    print("\n" + "="*70)
    print("CONTOH PENGGUNAAN")
    print("="*70)
    
    print("""
1. AUDIT KEUANGAN (Python Script):
   --------------------------------
   from audit_toolkit import (
       ExcelAuditProcessorV2, BUMDAnalyzer
   )
   
   # Baca file
   proc = ExcelAuditProcessorV2()
   df = proc.read_excel_multiheader('data.xlsx', [0, 1])
   
   # Proses
   proc.detect_and_convert_numbers(df)
   proc.calculate_financial_ratios(df)
   
   # Filter
   analyzer = BUMDAnalyzer(df)
   low_roa = analyzer.filter_by_roa(max_roa=5)
   
   # Export
   proc.export_clean('hasil.xlsx', low_roa)


2. AUDIT SPI (Python Script):
   ---------------------------
   from template_audit_spi import AuditSPI
   
   audit = AuditSPI(nama_entitas="PDAM XYZ")
   
   # Input data
   audit.input_penilaian(
       komponen='LINGKUNGAN_PENGENDALIAN',
       indikator='Integritas',
       nilai=4,
       keterangan='Sudah baik'
   )
   
   # Atau baca dari Excel
   audit.input_from_excel('data_spi.xlsx')
   
   # Hitung dan lapor
   audit.hitung_nilai_spi()
   audit.generate_laporan('hasil_spi.xlsx')


3. AUDIT KINERJA (Python Script):
   -------------------------------
   from template_audit_kinerja import AuditKinerja
   
   audit = AuditKinerja(tahun=2024)
   audit.load_data('data_kinerja.xlsx')
   audit.hitung_skor()
   
   # Get hasil
   top10 = audit.get_top_performer(10)
   bottom10 = audit.get_bottom_performer(10)
   
   # Export dan visualisasi
   audit.generate_laporan('hasil_kinerja.xlsx')
   audit.visualisasi('grafik')
    """)
    
    input("\nTekan Enter untuk kembali ke menu...")


def main():
    """Main loop"""
    while True:
        print_banner()
        print_menu()
        
        try:
            pilihan = input("\nPilih (1-5): ").strip()
            
            if pilihan == '1':
                run_audit_keuangan()
            elif pilihan == '2':
                run_audit_spi()
            elif pilihan == '3':
                run_audit_kinerja()
            elif pilihan == '4':
                show_examples()
            elif pilihan == '5':
                print("\n✅ Terima kasih telah menggunakan AI Audit Toolkit!")
                break
            else:
                print("\n✗ Pilihan tidak valid. Pilih 1-5.")
            
            input("\nTekan Enter untuk kembali ke menu...")
            
        except KeyboardInterrupt:
            print("\n\n✅ Keluar...")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
            input("\nTekan Enter untuk melanjutkan...")


# Shortcut untuk command line
def quick_run():
    """Quick run dari command line"""
    import sys
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == 'keuangan':
            print_banner()
            run_audit_keuangan()
            return
        elif arg == 'spi':
            print_banner()
            run_audit_spi()
            return
        elif arg == 'kinerja':
            print_banner()
            run_audit_kinerja()
            return
        elif arg == 'demo':
            print_banner()
            print("Menjalankan semua demo...")
            print("\n" + "="*70)
            os.system("python template_audit_spi.py demo")
            print("\n" + "="*70)
            os.system("python template_audit_kinerja.py demo")
            return
        elif arg in ['contoh', 'example', 'code']:
            show_examples()
            return
    
    # Jalankan menu interaktif
    main()


if __name__ == "__main__":
    quick_run()
