#!/usr/bin/env python
"""
Analisis Lengkap Indonesia - 34 Provinsi
"""

import sqlite3
import json
from collections import Counter, defaultdict

def analyze():
    print("="*70)
    print("  ANALISIS INDONESIA SABANG-MERAUKE")
    print("  34 Provinsi - Data BPS Real")
    print("="*70)
    
    conn = sqlite3.connect('logs/feedback/self_improve.db')
    cursor = conn.cursor()
    
    # Get Indonesia data (session_id like 'indonesia_%')
    cursor.execute("""
        SELECT user_input, user_feedback 
        FROM interactions 
        WHERE session_id LIKE 'indonesia_%'
    """)
    
    data = cursor.fetchall()
    
    # Counters
    provinsi = Counter()
    pulau = Counter()
    gender = Counter()
    umur = Counter()
    pendidikan = Counter()
    pekerjaan = Counter()
    ekonomi = Counter()
    emosi = Counter()
    suku = Counter()
    internet = Counter()
    
    feedback_by_region = defaultdict(lambda: {'pos': 0, 'neg': 0})
    
    total = len(data)
    positive = 0
    negative = 0
    
    for row in data:
        try:
            persona = json.loads(row[0])
            feedback = row[1]
            
            prov = persona.get('provinsi', 'Unknown')
            provinsi[prov] += 1
            
            pul = persona.get('pulau', 'Unknown')
            pulau[pul] += 1
            
            gender[persona.get('gender', 'Unknown')] += 1
            umur[persona.get('umur', 'Unknown')] += 1
            pendidikan[persona.get('pendidikan', 'Unknown')] += 1
            pekerjaan[persona.get('pekerjaan', 'Unknown')] += 1
            ekonomi[persona.get('ekonomi', 'Unknown')] += 1
            emosi[persona.get('emosi', 'Unknown')] += 1
            suku[persona.get('suku_dominan', 'Unknown')] += 1
            internet[persona.get('akses_internet', 'Unknown')] += 1
            
            if feedback == 1:
                positive += 1
                feedback_by_region[pul]['pos'] += 1
            else:
                negative += 1
                feedback_by_region[pul]['neg'] += 1
                
        except Exception as e:
            pass
    
    conn.close()
    
    # Print results
    print(f"\n  TOTAL: {total:,} interaksi")
    print(f"  Positive: {positive:,} ({positive/total*100:.1f}%)")
    print(f"  Negative: {negative:,} ({negative/total*100:.1f}%)")
    
    print(f"\n  [PULAU]")
    for p, count in pulau.most_common():
        pct = count / total * 100
        print(f"    {p}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  [TOP 10 PROVINSI]")
    for prov, count in provinsi.most_common(10):
        pct = count / total * 100
        print(f"    {prov}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  [GENDER]")
    for g, count in gender.most_common():
        pct = count / total * 100
        print(f"    {g}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  [UMUR]")
    for u, count in umur.most_common():
        pct = count / total * 100
        print(f"    {u}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  [PENDIDIKAN]")
    for edu, count in pendidikan.most_common():
        print(f"    {edu}: {count:,}")
    
    print(f"\n  [PEKERJAAN TOP 5]")
    for job, count in pekerjaan.most_common(5):
        print(f"    {job}: {count:,}")
    
    print(f"\n  [EKONOMI]")
    for econ, count in ekonomi.most_common():
        print(f"    {econ}: {count:,}")
    
    print(f"\n  [EMOSI TOP 5]")
    for em, count in emosi.most_common(5):
        print(f"    {em}: {count:,}")
    
    print(f"\n  [SUKU DOMINAN]")
    for s, count in suku.most_common():
        print(f"    {s}: {count:,}")
    
    print(f"\n  [AKSES INTERNET]")
    for inet, count in internet.most_common():
        print(f"    {inet}: {count:,}")
    
    print(f"\n  [FEEDBACK BY PULAU]")
    for pulau_name, stats in feedback_by_region.items():
        total_pulau = stats['pos'] + stats['neg']
        if total_pulau > 0:
            sat = stats['pos'] / total_pulau * 100
            print(f"    {pulau_name}: {sat:.1f}% satisfaction")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    analyze()
