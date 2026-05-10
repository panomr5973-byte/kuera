#!/usr/bin/env python3
"""
Template Audit Kinerja
Analisis kinerja organisasi/pejabat dengan scoring dan ranking
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Try import visualization
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class AuditKinerja:
    """Audit Kinerja dengan metodologi scoring"""
    
    def __init__(self, tahun=datetime.now().year):
        self.tahun = tahun
        self.data = None
        self.hasil = None
        
        # Indikator kinerja default
        self.indikator = {
            'KEUANGAN': {
                'nama': 'Kinerja Keuangan',
                'bobot': 0.30,
                'sub_indikator': {
                    'realisasi_anggaran': 0.40,
                    'efisiensi_biaya': 0.30,
                    'kemandirian': 0.30
                }
            },
            'PELAYANAN': {
                'nama': 'Kinerja Pelayanan',
                'bobot': 0.25,
                'sub_indikator': {
                    'kepuasan_pelanggan': 0.50,
                    'waktu_pelayanan': 0.30,
                    'keluhan_terselesaikan': 0.20
                }
            },
            'OPERASIONAL': {
                'nama': 'Kinerja Operasional',
                'bobot': 0.25,
                'sub_indikator': {
                    'volume_produksi': 0.40,
                    'kualitas_output': 0.35,
                    'penggunaan_kapasitas': 0.25
                }
            },
            'ORGANISASI': {
                'nama': 'Kinerja Organisasi',
                'bobot': 0.20,
                'sub_indikator': {
                    'disiplin_pegawai': 0.40,
                    'pengembangan_kompetensi': 0.30,
                    'pengurangan_turnover': 0.30
                }
            }
        }
    
    def load_data(self, filepath):
        """Load data kinerja dari Excel"""
        print(f"📂 Loading data: {filepath}")
        
        try:
            self.data = pd.read_excel(filepath)
            print(f"   ✓ {len(self.data)} entitas dimuat")
            print(f"   ✓ {len(self.data.columns)} kolom tersedia")
            return True
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
    
    def setup_indikator(self, indikator_dict):
        """Setup indikator custom"""
        self.indikator = indikator_dict
        print(f"   ✓ {len(indikator_dict)} indikator diatur")
    
    def hitung_skor(self):
        """Hitung skor kinerja untuk semua entitas"""
        if self.data is None:
            print("   ✗ Load data dulu dengan load_data()")
            return None
        
        print("\n📊 Menghitung skor kinerja...")
        
        hasil_list = []
        
        for idx, row in self.data.iterrows():
            entitas = row.get('nama', row.get('nama_entitas', f'Entitas_{idx}'))
            skor_detail = {}
            skor_total = 0
            
            # Hitung per aspek
            for kode_aspek, info_aspek in self.indikator.items():
                skor_aspek = 0
                
                for sub, bobot_sub in info_aspek['sub_indikator'].items():
                    nilai = row.get(sub, 0)
                    if pd.isna(nilai):
                        nilai = 0
                    skor_aspek += nilai * bobot_sub
                
                skor_bobot = skor_aspek * info_aspek['bobot']
                skor_total += skor_bobot
                
                skor_detail[kode_aspek] = {
                    'nilai': skor_aspek,
                    'bobot': info_aspek['bobot'],
                    'kontribusi': skor_bobot
                }
            
            hasil_list.append({
                'nama': entitas,
                'skor_total': skor_total,
                'kategori': self._kategorikan(skor_total),
                'detail': skor_detail
            })
        
        # Sort by score
        hasil_list.sort(key=lambda x: x['skor_total'], reverse=True)
        
        # Add ranking
        for i, h in enumerate(hasil_list, 1):
            h['ranking'] = i
        
        self.hasil = hasil_list
        
        print(f"   ✓ {len(hasil_list)} entitas dinilai")
        print(f"   ✓ Skor tertinggi: {hasil_list[0]['skor_total']:.2f}")
        print(f"   ✓ Skor terendah: {hasil_list[-1]['skor_total']:.2f}")
        
        return hasil_list
    
    def _kategorikan(self, skor):
        """Kategorikan skor kinerja"""
        if skor >= 90:
            return {'kelas': 'SANGAT BAIK', 'predikat': 'A', 'warna': 'HIJAU'}
        elif skor >= 80:
            return {'kelas': 'BAIK', 'predikat': 'B', 'warna': 'HIJAU'}
        elif skor >= 70:
            return {'kelas': 'CUKUP', 'predikat': 'C', 'warna': 'KUNING'}
        elif skor >= 60:
            return {'kelas': 'KURANG', 'predikat': 'D', 'warna': 'ORANGE'}
        else:
            return {'kelas': 'SANGAT KURANG', 'predikat': 'E', 'warna': 'MERAH'}
    
    def get_top_performer(self, n=10):
        """Get top n performer"""
        if not self.hasil:
            return []
        return self.hasil[:n]
    
    def get_bottom_performer(self, n=10):
        """Get bottom n performer"""
        if not self.hasil:
            return []
        return self.hasil[-n:]
    
    def get_by_kategori(self, predikat):
        """Filter by predikat (A/B/C/D/E)"""
        if not self.hasil:
            return []
        return [h for h in self.hasil if h['kategori']['predikat'] == predikat]
    
    def generate_laporan(self, output_file='laporan_kinerja.xlsx'):
        """Generate laporan lengkap"""
        if not self.hasil:
            print("   ✗ Hitung skor dulu dengan hitung_skor()")
            return
        
        print(f"\n📄 Generate laporan: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet 1: Ranking Lengkap
            ranking_data = []
            for h in self.hasil:
                row = {
                    'Ranking': h['ranking'],
                    'Nama': h['nama'],
                    'Skor Total': h['skor_total'],
                    'Predikat': h['kategori']['predikat'],
                    'Kategori': h['kategori']['kelas']
                }
                # Add aspek scores
                for aspek, detail in h['detail'].items():
                    row[f'Skor_{aspek}'] = detail['nilai']
                
                ranking_data.append(row)
            
            df_ranking = pd.DataFrame(ranking_data)
            df_ranking.to_excel(writer, sheet_name='Ranking', index=False)
            
            # Sheet 2: Top 10
            top10 = df_ranking.head(10)
            top10.to_excel(writer, sheet_name='Top_10', index=False)
            
            # Sheet 3: Bottom 10
            bottom10 = df_ranking.tail(10)
            bottom10.to_excel(writer, sheet_name='Bottom_10', index=False)
            
            # Sheet 4: Distribusi Kategori
            kategori_count = df_ranking['Predikat'].value_counts().sort_index()
            distribusi = pd.DataFrame({
                'Predikat': kategori_count.index,
                'Jumlah': kategori_count.values,
                'Persentase': (kategori_count.values / len(df_ranking) * 100).round(2)
            })
            distribusi.to_excel(writer, sheet_name='Distribusi', index=False)
            
            # Sheet 5: Statistik
            stats = {
                'Metrik': ['Rata-rata', 'Median', 'Min', 'Max', 'Std Dev'],
                'Nilai': [
                    df_ranking['Skor Total'].mean(),
                    df_ranking['Skor Total'].median(),
                    df_ranking['Skor Total'].min(),
                    df_ranking['Skor Total'].max(),
                    df_ranking['Skor Total'].std()
                ]
            }
            pd.DataFrame(stats).to_excel(writer, sheet_name='Statistik', index=False)
        
        print(f"   ✓ Laporan tersimpan dengan {len(df_ranking)} entitas")
    
    def visualisasi(self, output_prefix='kinerja'):
        """Generate visualisasi"""
        if not MATPLOTLIB_AVAILABLE:
            print("   ⚠️  Matplotlib tidak tersedia")
            return
        
        if not self.hasil:
            print("   ✗ Hitung skor dulu")
            return
        
        print("\n📊 Generate visualisasi...")
        
        # Extract data
        skor_list = [h['skor_total'] for h in self.hasil]
        predikat_list = [h['kategori']['predikat'] for h in self.hasil]
        
        # 1. Distribusi Skor
        plt.figure(figsize=(10, 6))
        plt.hist(skor_list, bins=20, color='skyblue', edgecolor='black')
        plt.axvline(x=np.mean(skor_list), color='r', linestyle='--', 
                   label=f'Rata-rata: {np.mean(skor_list):.1f}')
        plt.xlabel('Skor Kinerja')
        plt.ylabel('Jumlah Entitas')
        plt.title('Distribusi Skor Kinerja')
        plt.legend()
        plt.savefig(f'{output_prefix}_distribusi.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # 2. Pie Chart Predikat
        plt.figure(figsize=(8, 8))
        predikat_count = pd.Series(predikat_list).value_counts().sort_index()
        colors = {'A': 'green', 'B': 'lightgreen', 'C': 'yellow', 
                 'D': 'orange', 'E': 'red'}
        plt.pie(predikat_count, labels=predikat_count.index, autopct='%1.1f%%',
               colors=[colors.get(p, 'gray') for p in predikat_count.index])
        plt.title('Distribusi Predikat Kinerja')
        plt.savefig(f'{output_prefix}_predikat.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # 3. Top 10 Bar Chart
        plt.figure(figsize=(12, 6))
        top10 = self.hasil[:10]
        names = [h['nama'][:20] for h in top10]
        scores = [h['skor_total'] for h in top10]
        
        plt.barh(range(len(names)), scores, color='steelblue')
        plt.yticks(range(len(names)), names)
        plt.xlabel('Skor Kinerja')
        plt.title('Top 10 Performer')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(f'{output_prefix}_top10.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ Visualisasi tersimpan:")
        print(f"     • {output_prefix}_distribusi.png")
        print(f"     • {output_prefix}_predikat.png")
        print(f"     • {output_prefix}_top10.png")
    
    def print_ringkasan(self):
        """Print ringkasan ke console"""
        if not self.hasil:
            print("   ✗ Hitung skor dulu")
            return
        
        print("\n" + "="*60)
        print(f"LAPORAN AUDIT KINERJA - TAHUN {self.tahun}")
        print("="*60)
        
        print(f"\nTotal Entitas: {len(self.hasil)}")
        print(f"Rata-rata Skor: {np.mean([h['skor_total'] for h in self.hasil]):.2f}")
        
        # Distribusi
        predikat_count = {}
        for h in self.hasil:
            p = h['kategori']['predikat']
            predikat_count[p] = predikat_count.get(p, 0) + 1
        
        print("\nDistribusi Predikat:")
        for p in ['A', 'B', 'C', 'D', 'E']:
            if p in predikat_count:
                print(f"   {p}: {predikat_count[p]} entitas")
        
        print("\n" + "-"*60)
        print("TOP 5 PERFORMER:")
        print("-"*60)
        for h in self.hasil[:5]:
            print(f"{h['ranking']:2}. {h['nama'][:40]:<40} {h['skor_total']:6.2f} {h['kategori']['predikat']}")
        
        print("\n" + "-"*60)
        print("BOTTOM 5 PERFORMER:")
        print("-"*60)
        for h in self.hasil[-5:]:
            print(f"{h['ranking']:2}. {h['nama'][:40]:<40} {h['skor_total']:6.2f} {h['kategori']['predikat']}")


def demo():
    """Demo dengan data sample"""
    print("="*60)
    print("TEMPLATE AUDIT KINERJA - DEMO")
    print("="*60)
    
    # Buat data sample
    np.random.seed(42)
    n = 50
    
    data_sample = {
        'nama': [f'BUMD_{i:02d}' for i in range(1, n+1)],
        'realisasi_anggaran': np.random.uniform(70, 100, n),
        'efisiensi_biaya': np.random.uniform(60, 95, n),
        'kemandirian': np.random.uniform(50, 90, n),
        'kepuasan_pelanggan': np.random.uniform(65, 95, n),
        'waktu_pelayanan': np.random.uniform(60, 100, n),
        'keluhan_terselesaikan': np.random.uniform(70, 100, n),
        'volume_produksi': np.random.uniform(75, 100, n),
        'kualitas_output': np.random.uniform(70, 95, n),
        'penggunaan_kapasitas': np.random.uniform(60, 95, n),
        'disiplin_pegawai': np.random.uniform(80, 100, n),
        'pengembangan_kompetensi': np.random.uniform(60, 90, n),
        'pengurangan_turnover': np.random.uniform(70, 95, n)
    }
    
    df = pd.DataFrame(data_sample)
    df.to_excel('data_kinerja_sample.xlsx', index=False)
    print("   ✓ Data sample dibuat: data_kinerja_sample.xlsx")
    
    # Proses
    audit = AuditKinerja(tahun=2024)
    audit.load_data('data_kinerja_sample.xlsx')
    audit.hitung_skor()
    audit.print_ringkasan()
    audit.generate_laporan('laporan_kinerja_sample.xlsx')
    
    if MATPLOTLIB_AVAILABLE:
        audit.visualisasi('sample')
    
    print("\n" + "="*60)
    print("✅ Demo selesai!")
    print("="*60)


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo()
        return
    
    print("="*60)
    print("AUDIT KINERJA - TEMPLATE")
    print("="*60)
    print("\nCara penggunaan:")
    print("1. Siapkan file Excel dengan kolom indikator kinerja")
    print("2. Jalankan dalam script Python:")
    print("""
   from template_audit_kinerja import AuditKinerja
   
   audit = AuditKinerja(tahun=2024)
   audit.load_data('data_kinerja.xlsx')
   audit.hitung_skor()
   audit.generate_laporan('hasil_kinerja.xlsx')
   audit.visualisasi('grafik_kinerja')
    """)
    print("\n3. Atau jalankan demo: python template_audit_kinerja.py demo")


if __name__ == "__main__":
    main()
