#!/usr/bin/env python3
"""
Template Audit SPI (Sistem Pengendalian Intern)
Berdasarkan COSO Framework untuk Government Audit Agency
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


class AuditSPI:
    """Audit Sistem Pengendalian Intern berbasis COSO Framework"""
    
    def __init__(self, nama_entitas=""):
        self.nama_entitas = nama_entitas
        self.data = []
        self.hasil = {}
        
        # COSO Components
        self.komponen_spi = {
            'LINGKUNGAN_PENGENDALIAN': {
                'nama': 'Lingkungan Pengendalian',
                'bobot': 0.20,
                'indikator': [
                    'Integritas dan Nilai Etika',
                    'Struktur Organisasi',
                    'Kebijakan SDM',
                    'Filosofi Manajemen',
                    'Pemisahan Tugas'
                ]
            },
            'PENILAIAN_RISIKO': {
                'nama': 'Penilaian Risiko',
                'bobot': 0.20,
                'indikator': [
                    'Identifikasi Risiko',
                    'Analisis Risiko',
                    'Penanganan Risiko',
                    'Pemantauan Risiko'
                ]
            },
            'KEGIATAN_PENGENDALIAN': {
                'nama': 'Kegiatan Pengendalian',
                'bobot': 0.25,
                'indikator': [
                    'Pengendalian Keuangan',
                    'Pengendalian Operasional',
                    'Pengendalian Kepatuhan',
                    'Pengendalian Akses'
                ]
            },
            'INFORMASI_KOMUNIKASI': {
                'nama': 'Informasi dan Komunikasi',
                'bobot': 0.20,
                'indikator': [
                    'Sistem Informasi',
                    'Laporan Internal',
                    'Komunikasi Eksternal',
                    'Dokumentasi'
                ]
            },
            'PEMANTAUAN': {
                'nama': 'Pemantauan Berkelanjutan',
                'bobot': 0.15,
                'indikator': [
                    'Audit Internal',
                    'Review Berkala',
                    'Tindak Lanjut Temuan',
                    'Evaluasi Kinerja'
                ]
            }
        }
    
    def input_penilaian(self, komponen, indikator, nilai, keterangan=""):
        """Input hasil penilaian
        
        Args:
            komponen: Kode komponen SPI (misal: 'LINGKUNGAN_PENGENDALIAN')
            indikator: Nama indikator
            nilai: 1-5 (1=Sangat Lemah, 5=Sangat Baik)
            keterangan: Catatan tambahan
        """
        self.data.append({
            'komponen': komponen,
            'indikator': indikator,
            'nilai': nilai,
            'keterangan': keterangan,
            'tanggal': datetime.now()
        })
    
    def input_from_excel(self, filepath):
        """Baca data penilaian dari Excel"""
        print(f"📂 Membaca file penilaian: {filepath}")
        
        try:
            df = pd.read_excel(filepath)
            required_cols = ['komponen', 'indikator', 'nilai']
            
            if not all(col in df.columns for col in required_cols):
                print("   ✗ Format file tidak sesuai. Kolom yang diperlukan:")
                print("      - komponen")
                print("      - indikator")
                print("      - nilai")
                print("      - keterangan (opsional)")
                return False
            
            for _, row in df.iterrows():
                self.input_penilaian(
                    komponen=row['komponen'],
                    indikator=row['indikator'],
                    nilai=row['nilai'],
                    keterangan=row.get('keterangan', '')
                )
            
            print(f"   ✓ {len(df)} penilaian dimuat")
            return True
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
    
    def hitung_nilai_spi(self):
        """Hitung nilai SPI per komponen dan keseluruhan"""
        print("\n📊 Menghitung Nilai SPI...")
        
        df = pd.DataFrame(self.data)
        if df.empty:
            print("   ✗ Tidak ada data penilaian")
            return None
        
        hasil = {}
        nilai_total = 0
        
        for kode, info in self.komponen_spi.items():
            data_komponen = df[df['komponen'] == kode]
            
            if not data_komponen.empty:
                rata2 = data_komponen['nilai'].mean()
                bobot_nilai = rata2 * info['bobot']
                nilai_total += bobot_nilai
                
                hasil[kode] = {
                    'nama': info['nama'],
                    'rata_rata': rata2,
                    'bobot': info['bobot'],
                    'nilai_bobot': bobot_nilai,
                    'jumlah_indikator': len(data_komponen),
                    'detail': data_komponen.to_dict('records')
                }
        
        # Kategori SPI
        kategori = self._kategorikan_spi(nilai_total)
        
        self.hasil = {
            'nilai_total': nilai_total,
            'kategori': kategori,
            'komponen': hasil,
            'rekomendasi': self._generate_rekomendasi(hasil)
        }
        
        return self.hasil
    
    def _kategorikan_spi(self, nilai):
        """Kategorikan tingkat SPI"""
        if nilai >= 4.5:
            return {'tingkat': 'SANGAT BAIK', 'warna': 'HIJAU', 'deskripsi': 'SPI sangat efektif'}
        elif nilai >= 3.5:
            return {'tingkat': 'BAIK', 'warna': 'HIJAU', 'deskripsi': 'SPI efektif dengan sedikit kelemahan'}
        elif nilai >= 2.5:
            return {'tingkat': 'CUKUP', 'warna': 'KUNING', 'deskripsi': 'SPI cukup efektif, perlu perbaikan'}
        elif nilai >= 1.5:
            return {'tingkat': 'LEMAH', 'warna': 'ORANGE', 'deskripsi': 'SPI lemah, perlu perbaikan signifikan'}
        else:
            return {'tingkat': 'SANGAT LEMAH', 'warna': 'MERAH', 'deskripsi': 'SPI sangat lemah, risiko tinggi'}
    
    def _generate_rekomendasi(self, hasil_komponen):
        """Generate rekomendasi berdasarkan kelemahan"""
        rekomendasi = []
        
        for kode, data in hasil_komponen.items():
            if data['rata_rata'] < 3.0:
                rekomendasi.append({
                    'komponen': data['nama'],
                    'nilai': data['rata_rata'],
                    'rekomendasi': self._get_rekomendasi_komponen(kode),
                    'prioritas': 'TINGGI' if data['rata_rata'] < 2.0 else 'SEDANG'
                })
        
        return rekomendasi
    
    def _get_rekomendasi_komponen(self, kode):
        """Get rekomendasi spesifik per komponen"""
        rekomendasi_map = {
            'LINGKUNGAN_PENGENDALIAN': [
                'Memperkuat komitmen pimpinan terhadap integritas',
                'Merevisi struktur organisasi untuk pemisahan tugas',
                'Menyusun kebijakan SDM yang lebih ketat'
            ],
            'PENILAIAN_RISIKO': [
                'Menyusun register risiko secara komprehensif',
                'Melakukan risk assessment berkala',
                'Menetapkan mitigasi risiko yang jelas'
            ],
            'KEGIATAN_PENGENDALIAN': [
                'Memperketat pengendalian keuangan',
                'Menerapkan SOP operasional standar',
                'Memperkuat pengendalian akses sistem'
            ],
            'INFORMASI_KOMUNIKASI': [
                'Meningkatkan sistem informasi manajemen',
                'Menyusun format laporan standar',
                'Memperbaiki dokumentasi kegiatan'
            ],
            'PEMANTAUAN': [
                'Menguatkan fungsi audit internal',
                'Menjadwalkan review berkala',
                'Meningkatkan tindak lanjut temuan'
            ]
        }
        return rekomendasi_map.get(kode, ['Perlu evaluasi lebih lanjut'])
    
    def generate_laporan(self, output_file='laporan_spi.xlsx'):
        """Generate laporan Excel lengkap"""
        if not self.hasil:
            print("   ✗ Hitung nilai SPI dulu dengan hitung_nilai_spi()")
            return
        
        print(f"\n📄 Generate laporan: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet 1: Ringkasan
            ringkasan = pd.DataFrame({
                'Item': ['Nama Entitas', 'Tanggal Penilaian', 'Nilai SPI Total', 
                        'Kategori', 'Status'],
                'Nilai': [
                    self.nama_entitas,
                    datetime.now().strftime('%Y-%m-%d'),
                    f"{self.hasil['nilai_total']:.2f}",
                    self.hasil['kategori']['tingkat'],
                    self.hasil['kategori']['deskripsi']
                ]
            })
            ringkasan.to_excel(writer, sheet_name='Ringkasan', index=False)
            
            # Sheet 2: Detail Komponen
            detail_rows = []
            for kode, data in self.hasil['komponen'].items():
                detail_rows.append({
                    'Komponen': data['nama'],
                    'Nilai Rata-rata': data['rata_rata'],
                    'Bobot': data['bobot'],
                    'Nilai Bobot': data['nilai_bobot'],
                    'Jumlah Indikator': data['jumlah_indikator']
                })
            
            detail_df = pd.DataFrame(detail_rows)
            detail_df.to_excel(writer, sheet_name='Detail_Komponen', index=False)
            
            # Sheet 3: Rekomendasi
            if self.hasil['rekomendasi']:
                rekom_df = pd.DataFrame(self.hasil['rekomendasi'])
                rekom_df.to_excel(writer, sheet_name='Rekomendasi', index=False)
            
            # Sheet 4: Data Mentah
            if self.data:
                raw_df = pd.DataFrame(self.data)
                raw_df.to_excel(writer, sheet_name='Data_Penilaian', index=False)
        
        print(f"   ✓ Laporan tersimpan")
    
    def print_ringkasan(self):
        """Print ringkasan ke console"""
        if not self.hasil:
            print("   ✗ Hitung nilai SPI dulu")
            return
        
        print("\n" + "="*60)
        print(f"LAPORAN AUDIT SPI - {self.nama_entitas}")
        print("="*60)
        
        print(f"\nNilai SPI Total: {self.hasil['nilai_total']:.2f} / 5.00")
        print(f"Kategori: {self.hasil['kategori']['tingkat']}")
        print(f"Status: {self.hasil['kategori']['deskripsi']}")
        
        print("\nDetail per Komponen:")
        print("-" * 60)
        for kode, data in self.hasil['komponen'].items():
            bar = "█" * int(data['rata_rata']) + "░" * (5 - int(data['rata_rata']))
            print(f"{data['nama'][:30]:<30} [{bar}] {data['rata_rata']:.2f}")
        
        if self.hasil['rekomendasi']:
            print("\nRekomendasi Prioritas:")
            print("-" * 60)
            for i, rec in enumerate(self.hasil['rekomendasi'][:3], 1):
                print(f"{i}. [{rec['prioritas']}] {rec['komponen']}")
                print(f"   Nilai: {rec['nilai']:.2f}")
                for r in rec['rekomendasi'][:2]:
                    print(f"   • {r}")


def demo():
    """Demo penggunaan Audit SPI"""
    print("="*60)
    print("TEMPLATE AUDIT SPI - DEMO")
    print("="*60)
    
    # Buat instance
    audit = AuditSPI(nama_entitas="PDAM Tirta Sample")
    
    # Simulasi input data
    print("\n📝 Simulasi input penilaian...")
    
    # Data sample (dalam praktek, baca dari Excel)
    sample_data = [
        ('LINGKUNGAN_PENGENDALIAN', 'Integritas dan Nilai Etika', 4, 'Sudah baik'),
        ('LINGKUNGAN_PENGENDALIAN', 'Struktur Organisasi', 3, 'Perlu penyesuaian'),
        ('PENILAIAN_RISIKO', 'Identifikasi Risiko', 2, 'Belum komprehensif'),
        ('PENILAIAN_RISIKO', 'Analisis Risiko', 2, 'Belum sistematis'),
        ('KEGIATAN_PENGENDALIAN', 'Pengendalian Keuangan', 4, 'SOP sudah ada'),
        ('INFORMASI_KOMUNIKASI', 'Sistem Informasi', 3, 'Perlu upgrade'),
        ('PEMANTAUAN', 'Audit Internal', 3, 'Jadwal belum rutin'),
    ]
    
    for komponen, indikator, nilai, ket in sample_data:
        audit.input_penilaian(komponen, indikator, nilai, ket)
    
    print(f"   ✓ {len(sample_data)} penilaian diinput")
    
    # Hitung dan tampilkan hasil
    audit.hitung_nilai_spi()
    audit.print_ringkasan()
    audit.generate_laporan('laporan_spi_sample.xlsx')
    
    print("\n" + "="*60)
    print("✅ Demo selesai!")
    print("   File output: laporan_spi_sample.xlsx")
    print("="*60)


def main():
    """Main function dengan menu"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo()
        return
    
    print("="*60)
    print("AUDIT SPI - SISTEM PENGENDALIAN INTERN")
    print("="*60)
    print("\nCara penggunaan:")
    print("1. Buat file Excel dengan kolom: komponen, indikator, nilai, keterangan")
    print("2. Jalankan: python template_audit_spi.py")
    print("3. Atau untuk demo: python template_audit_spi.py demo")
    print("\nKomponen SPI yang tersedia:")
    for kode, info in AuditSPI().komponen_spi.items():
        print(f"   • {kode}: {info['nama']}")


if __name__ == "__main__":
    main()
