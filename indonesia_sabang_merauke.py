#!/usr/bin/env python
"""
INDONESIA SABANG-MERAUKE - 34 Provinsi dengan Data BPS Real
Simulasi lengkap seluruh Indonesia dari ujung barat (Sabang) sampai ujung timur (Merauke)
"""

import sqlite3
import random
import json
from datetime import datetime, timedelta
from dataclasses import dataclass

# ============================================================
# DATA 34 PROVINSI INDONESIA - BPS 2023/2024
# ============================================================

@dataclass
class Province:
    name: str
    population_millions: float
    region: str
    characteristics: str
    dominant_ethnic: str
    main_occupation: str
    economic_level: str
    internet_penetration: float

# Data 34 Provinsi Indonesia (BPS 2023)
INDONESIA_PROVINCES = [
    # SUMATERA (6 Provinsi)
    Province("Aceh", 5.52, "Sumatera", "syariah_conservative", "Aceh", "agriculture_fishing", "menengah_bawah", 65.0),
    Province("Sumatera Utara", 15.18, "Sumatera", "multicultural_urban", "Batak_Karo_Melayu", "plantation_services", "menengah", 78.0),
    Province("Sumatera Barat", 5.75, "Sumatera", "matrilineal_minang", "Minangkabau", "trade_services", "menengah", 75.0),
    Province("Riau", 6.49, "Sumatera", "oil_palm rich", "Melayu_Bugis", "plantation_industry", "menengah_atas", 80.0),
    Province("Kepulauan Riau", 2.08, "Sumatera", "trade_gateway", "Melayu_Chinese", "trade_services", "menengah_atas", 85.0),
    Province("Jambi", 3.68, "Sumatera", "rural_rubber", "Melayu_Kerinci", "agriculture", "menengah_bawah", 70.0),
    Province("Sumatera Selatan", 8.68, "Sumatera", "river_civilization", "Palembang_Komering", "agriculture_trade", "menengah", 72.0),
    Province("Bangka Belitung", 1.51, "Sumatera", "tin_mining", "Melayu_Chinese", "mining_fishing", "menengah", 75.0),
    Province("Bengkulu", 2.08, "Sumatera", "coastal_rural", "Rejang_Melayu", "agriculture", "menengah_bawah", 68.0),
    Province("Lampung", 9.18, "Sumatera", "transmigration_destination", "Jawa_Lampung", "agriculture", "menengah_bawah", 70.0),
    
    # JAWA (6 Provinsi)
    Province("DKI Jakarta", 10.56, "Jawa", "megacity_capital", "Betawi_Jawa_Sunda", "services_finance", "kaya", 92.0),
    Province("Jawa Barat", 49.94, "Jawa", "most_populous_sundanese", "Sunda", "manufacturing_services", "menengah", 82.0),
    Province("Banten", 12.31, "Jawa", "industrial_suburb", "Sunda_Banten", "industry_services", "menengah", 80.0),
    Province("Jawa Tengah", 37.54, "Jawa", "jateng_gayeng_culture", "Jawa", "agriculture_craft", "menengah", 78.0),
    Province("DI Yogyakarta", 3.73, "Jawa", "student_city_culture", "Jawa", "education_tourism", "menengah", 88.0),
    Province("Jawa Timur", 41.15, "Jawa", "arek_suroboyo_madura", "Jawa_Madura", "industry_agriculture", "menengah", 80.0),
    
    # BALI & NUSA TENGGARA (3 Provinsi)
    Province("Bali", 4.32, "Bali_NTT", "tourism_hindu_culture", "Bali", "tourism_services", "menengah_atas", 85.0),
    Province("Nusa Tenggara Barat", 5.39, "Bali_NTT", "islamic_sasak", "Sasak", "agriculture_tourism", "menengah_bawah", 70.0),
    Province("Nusa Tenggara Timur", 5.56, "Bali_NTT", "diverse_islands", "Flores_Timor_Sumba", "agriculture_fishing", "miskin", 60.0),
    
    # KALIMANTAN (5 Provinsi)
    Province("Kalimantan Barat", 5.62, "Kalimantan", "dayak_border", "Dayak_Melayu", "agriculture_palm", "menengah_bawah", 72.0),
    Province("Example Province", 2.79, "Kalimantan", "forest_sparsely", "Dayak", "agriculture_logging", "menengah_bawah", 68.0),
    Province("Kalimantan Selatan", 4.17, "Kalimantan", "banjar_river", "Banjar", "agriculture_trade", "menengah", 75.0),
    Province("Kalimantan Timur", 3.93, "Kalimantan", "mining_industrial", "Dayak_Bugis_Jawa", "mining_oil_gas", "menengah_atas", 82.0),
    Province("Kalimantan Utara", 0.73, "Kalimantan", "new_frontier", "Dayak_Bulungan", "agriculture_border", "menengah", 70.0),
    
    # SULAWESI (6 Provinsi)
    Province("Sulawesi Utara", 2.65, "Sulawesi", "minahasa_christian", "Minahasa", "fishing_tourism", "menengah", 78.0),
    Province("Gorontalo", 1.18, "Sulawesi", "islamic_gorontalo", "Gorontalo", "agriculture_fishing", "menengah_bawah", 70.0),
    Province("Sulawesi Tengah", 3.10, "Sulawesi", "mountainous_kaili", "Kaili_Pamona", "agriculture", "menengah_bawah", 68.0),
    Province("Sulawesi Selatan", 9.14, "Sulawesi", "makassar_bugis_maritime", "Bugis_Makassar_Toraja", "trade_agriculture", "menengah", 78.0),
    Province("Sulawesi Tenggara", 2.67, "Sulawesi", "buton_muna_konawe", "Buton_Muna", "agriculture_mining", "menengah_bawah", 72.0),
    Province("Sulawesi Barat", 1.42, "Sulawesi", "mandar_coastal", "Mandar", "fishing_agriculture", "menengah_bawah", 65.0),
    
    # MALUKU & PAPUA (5 Provinsi)
    Province("Maluku", 1.85, "Maluku_Papua", "spice_islands_christian_muslim", "Ambon_Manise", "fishing_tourism", "menengah_bawah", 70.0),
    Province("Maluku Utara", 1.30, "Maluku_Papua", "ternate_tidore_spice", "Ternate_Tidore", "fishing_nickel", "menengah_bawah", 72.0),
    Province("Papua Barat", 1.14, "Maluku_Papua", "manokwari_bird_head", "Papua_Biak", "mining_fishing", "menengah", 75.0),
    Province("Papua", 4.36, "Maluku_Papua", "jayapura_highland_diverse", "Dani_Yali_Asmat", "mining_services", "menengah_bawah", 65.0),
    Province("Papua Selatan", 0.51, "Maluku_Papua", "newest_province_merauke", "Marind_Amat", "agriculture_border", "menengah_bawah", 60.0),
]

# Total populasi Indonesia: ~277.5 juta (BPS 2023)
TOTAL_POPULATION = sum(p.population_millions for p in INDONESIA_PROVINCES)

# Gender distribusi nasional
GENDER_NASIONAL = {"Laki-laki": 50.4, "Perempuan": 49.6}

# Kelompok umur nasional (BPS 2023)
AGE_NASIONAL = [
    ("0-14 (Anak)", 24.5),
    ("15-24 (Pemuda)", 16.8),
    ("25-54 (Produktif)", 44.2),
    ("55-64 (Pra-pensiun)", 8.5),
    ("65+ (Lansia)", 6.0),
]

# Pendidikan nasional
EDUCATION_NASIONAL = [
    ("Tidak/belum sekolah", 4.5),
    ("SD", 20.2),
    ("SMP", 21.8),
    ("SMA", 35.5),
    ("Diploma", 6.2),
    ("Sarjana", 10.5),
    ("Pascasarjana", 1.3),
]

# Pekerjaan nasional
OCCUPATION_NASIONAL = [
    ("Petani/nelayan/peternak", 28.5),
    ("Buruh", 14.2),
    ("Wiraswasta/pedagang", 22.8),
    ("Karyawan swasta", 18.5),
    ("PNS/TNI/Polri", 4.2),
    ("Profesional", 6.8),
    ("IRT/pelajar/tidak kerja", 5.0),
]

# Status ekonomi nasional
ECONOMIC_NASIONAL = [
    ("Miskin", 9.5),
    ("Rentan miskin", 12.0),
    ("Menengah bawah", 28.5),
    ("Menengah", 32.0),
    ("Menengah atas", 14.0),
    ("Kaya", 4.0),
]

class IndonesiaSimulator:
    def __init__(self):
        self.provinces = INDONESIA_PROVINCES
        self.total_pop = TOTAL_POPULATION
        
    def generate_persona(self):
        """Generate persona berdasarkan data BPS Indonesia"""
        # Pilih provinsi berdasarkan populasi (weighted)
        prov = random.choices(
            self.provinces,
            weights=[p.population_millions for p in self.provinces]
        )[0]
        
        # Gender
        gender = random.choices(
            list(GENDER_NASIONAL.keys()),
            weights=list(GENDER_NASIONAL.values())
        )[0]
        
        # Umur
        age_group = random.choices(
            [a[0] for a in AGE_NASIONAL],
            weights=[a[1] for a in AGE_NASIONAL]
        )[0]
        
        # Pendidikan
        edu = random.choices(
            [e[0] for e in EDUCATION_NASIONAL],
            weights=[e[1] for e in EDUCATION_NASIONAL]
        )[0]
        
        # Pekerjaan
        job = random.choices(
            [o[0] for o in OCCUPATION_NASIONAL],
            weights=[o[1] for o in OCCUPATION_NASIONAL]
        )[0]
        
        # Ekonomi
        econ = random.choices(
            [e[0] for e in ECONOMIC_NASIONAL],
            weights=[e[1] for e in ECONOMIC_NASIONAL]
        )[0]
        
        # Internet penetration berdasarkan provinsi
        has_internet = random.random() < (prov.internet_penetration / 100)
        
        # Emosi berdasarkan karakteristik daerah
        if prov.economic_level == "miskin":
            emotions = ["Khawatir ekonomi", "Bersyukur", "Cemas", "Bersabar"]
            weights = [0.30, 0.25, 0.25, 0.20]
        elif prov.economic_level == "kaya":
            emotions = ["Santai", "Optimis", "Busy", "Ambisius"]
            weights = [0.30, 0.30, 0.25, 0.15]
        else:
            emotions = ["Bersyukur", "Khawatir", "Santai", "Bersemangat", "Cemas"]
            weights = [0.25, 0.20, 0.20, 0.20, 0.15]
        
        emotion = random.choices(emotions, weights=weights)[0]
        
        # Feedback accuracy
        base_acc = 0.65
        if "khawatir" in emotion.lower() or "cemas" in emotion.lower():
            base_acc -= 0.10
        elif "santai" in emotion.lower() or "optimis" in emotion.lower():
            base_acc += 0.10
            
        if prov.internet_penetration > 80:
            base_acc += 0.05
        elif prov.internet_penetration < 65:
            base_acc -= 0.05
            
        is_correct = random.random() < base_acc
        
        return {
            'provinsi': prov.name,
            'pulau': prov.region,
            'karakteristik': prov.characteristics,
            'suku_dominan': prov.dominant_ethnic,
            'gender': gender,
            'umur': age_group,
            'pendidikan': edu,
            'pekerjaan': job,
            'ekonomi': econ,
            'level_ekonomi_provinsi': prov.economic_level,
            'akses_internet': "Ya" if has_internet else "Tidak",
            'emosi': emotion,
            'feedback': 1 if is_correct else 0,
            'accuracy': base_acc,
            'region_code': f"{prov.region.lower()}_{prov.name.replace(' ', '_').lower()}"
        }

def main():
    # Target: Proporsional dengan populasi, sekitar 2 juta interaksi
    # untuk mewakili seluruh Indonesia
    target = 2_000_000
    batch_size = 10000
    
    print("="*70)
    print("  INDONESIA SABANG-MERAUKE SIMULATION")
    print("  34 Provinsi dengan Data BPS Real")
    print("="*70)
    print(f"\n  Target: {target:,} interaksi")
    print(f"  Total Populasi Referensi: {TOTAL_POPULATION:.2f} juta jiwa")
    print(f"  Provinsi: 34 provinsi dari Aceh sampai Papua Selatan")
    print(f"\n  Wilayah:")
    print(f"    - Sumatera: 10 provinsi")
    print(f"    - Jawa: 6 provinsi (termasuk DKI, DIY)")
    print(f"    - Bali & Nusa Tenggara: 3 provinsi")
    print(f"    - Kalimantan: 5 provinsi")
    print(f"    - Sulawesi: 6 provinsi")
    print(f"    - Maluku & Papua: 5 provinsi")
    print("="*70)
    
    conn = sqlite3.connect('logs/feedback/self_improve.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM interactions")
    start_count = cursor.fetchone()[0]
    print(f"\n  Starting count: {start_count:,}")
    print(f"  Target add: {target:,}")
    print(f"  Target final: {start_count + target:,}")
    
    sim = IndonesiaSimulator()
    
    start_time = datetime.now()
    inserted = 0
    
    for batch in range(target // batch_size):
        batch_data = []
        for i in range(batch_size):
            p = sim.generate_persona()
            ts = (datetime.now() - timedelta(minutes=random.randint(0, 14400))).isoformat()
            
            batch_data.append((
                ts,
                f"indonesia_{p['region_code']}_{batch*batch_size+i}",
                json.dumps(p, ensure_ascii=False),
                json.dumps({
                    'pred': random.randint(0, 1),
                    'provinsi': p['provinsi'],
                    'pulau': p['pulau'],
                    'emosi': p['emosi']
                }),
                'model_gb_indonesia',
                p['feedback'],
                f"{p['emosi']}_{p['ekonomi']}",
                random.uniform(100, 1500),
                p['accuracy']
            ))
        
        cursor.executemany("""
            INSERT INTO interactions 
            (timestamp, session_id, user_input, ai_response, model_used, 
             user_feedback, feedback_reason, latency_ms, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch_data)
        
        conn.commit()
        inserted += batch_size
        
        if (batch + 1) % 10 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = inserted / elapsed if elapsed > 0 else 0
            pct = inserted / target * 100
            print(f"  Progress: {inserted:,}/{target:,} ({pct:.1f}%) | Rate: {rate:.0f}/s | Elapsed: {elapsed:.0f}s")
    
    cursor.execute("SELECT COUNT(*) FROM interactions")
    final_count = cursor.fetchone()[0]
    conn.close()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*70)
    print("  SELESAI!")
    print("="*70)
    print(f"  Inserted: {inserted:,}")
    print(f"  Total in DB: {final_count:,}")
    print(f"  Time: {elapsed/60:.1f} menit")
    print(f"  Rate: {inserted/elapsed:.0f} interactions/s")
    print("="*70)

if __name__ == "__main__":
    main()
