#!/usr/bin/env python
"""
Analisis Data Kalimantan - Visualisasi demografi dari BPS
"""

import sqlite3
import json
from collections import Counter

def analyze():
    print("="*70)
    print("  ANALISIS DATA KALIMANTAN - BPS")
    print("="*70)
    
    conn = sqlite3.connect('logs/feedback/self_improve.db')
    cursor = conn.cursor()
    
    # Get Kalimantan data (yang session_id nya mengandung 'kalimantan')
    cursor.execute("""
        SELECT user_input, user_feedback 
        FROM interactions 
        WHERE session_id LIKE 'kalimantan_%'
    """)
    
    data = cursor.fetchall()
    
    # Counters
    provinsi = Counter()
    gender = Counter()
    umur = Counter()
    pekerjaan = Counter()
    pendidikan = Counter()
    ekonomi = Counter()
    etnis = Counter()
    emosi = Counter()
    feedback_by_province = {}
    
    total = len(data)
    positive = 0
    negative = 0
    
    for row in data:
        try:
            persona = json.loads(row[0])
            feedback = row[1]
            
            prov = persona.get('provinsi', 'Unknown')
            provinsi[prov] += 1
            
            gender[persona.get('gender', 'Unknown')] += 1
            umur[persona.get('umur', 'Unknown')] += 1
            pekerjaan[persona.get('pekerjaan', 'Unknown')] += 1
            pendidikan[persona.get('pendidikan', 'Unknown')] += 1
            ekonomi[persona.get('ekonomi', 'Unknown')] += 1
            etnis[persona.get('etnis', 'Unknown')] += 1
            emosi[persona.get('emosi', 'Unknown')] += 1
            
            # Feedback by province
            if prov not in feedback_by_province:
                feedback_by_province[prov] = {'pos': 0, 'neg': 0}
            if feedback == 1:
                feedback_by_province[prov]['pos'] += 1
                positive += 1
            else:
                feedback_by_province[prov]['neg'] += 1
                negative += 1
                
        except:
            pass
    
    conn.close()
    
    # Print results
    print(f"\n  TOTAL DATA: {total:,} interaksi")
    print(f"  Positive: {positive:,} ({positive/total*100:.1f}%)")
    print(f"  Negative: {negative:,} ({negative/total*100:.1f}%)")
    
    print(f"\n  📍 DISTRIBUSI PROVINSI:")
    for prov, count in provinsi.most_common():
        pct = count / total * 100
        print(f"    {prov}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  👥 DISTRIBUSI GENDER:")
    for g, count in gender.most_common():
        pct = count / total * 100
        print(f"    {g}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  🎂 DISTRIBUSI UMUR:")
    for u, count in umur.most_common():
        pct = count / total * 100
        print(f"    {u}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  💼 TOP 5 PEKERJAAN:")
    for job, count in pekerjaan.most_common(5):
        pct = count / total * 100
        print(f"    {job}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  🎓 TOP 5 PENDIDIKAN:")
    for edu, count in pendidikan.most_common(5):
        pct = count / total * 100
        print(f"    {edu}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  💰 DISTRIBUSI EKONOMI:")
    for econ, count in ekonomi.most_common():
        pct = count / total * 100
        print(f"    {econ}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  🏛️ DISTRIBUSI ETNIS:")
    for eth, count in etnis.most_common():
        pct = count / total * 100
        print(f"    {eth}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  😊 TOP 5 EMOSI:")
    for em, count in emosi.most_common(5):
        pct = count / total * 100
        print(f"    {em}: {count:,} ({pct:.1f}%)")
    
    print(f"\n  📊 FEEDBACK BY PROVINCE:")
    for prov, stats in feedback_by_province.items():
        total_prov = stats['pos'] + stats['neg']
        if total_prov > 0:
            sat = stats['pos'] / total_prov * 100
            print(f"    {prov}: {sat:.1f}% satisfaction ({stats['pos']}/{total_prov})")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    analyze()
