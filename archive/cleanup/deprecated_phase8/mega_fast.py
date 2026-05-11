#!/usr/bin/env python
"""
MEGA FAST - 1 Juta Interaksi dalam waktu singkat
Direct database insertion tanpa API calls
"""

import sqlite3
import random
import json
from datetime import datetime, timedelta

# Demographics
GENDERS = [("Laki-laki", 50.4), ("Perempuan", 49.6), ("Non-biner", 0.05)]
AGES = [("Anak", 25), ("Remaja", 15), ("Dewasa Muda", 18), ("Dewasa", 16), 
        ("Paruh Baya", 14), ("Pra-pensiun", 7), ("Lansia", 4), ("Manula", 1)]
SOCIAL = [("Pelajar", 15), ("Karyawan", 25), ("Wiraswasta", 10), ("Profesional", 8),
          ("IRT", 12), ("Pensiunan", 5), ("Pengangguran", 3), ("Lainnya", 10)]
EMOTIONS = [("Bahagia", 20, 0.85), ("Santai", 15, 0.80), ("Netral", 18, 0.65),
            ("Cemas", 12, 0.50), ("Stres", 10, 0.40), ("Marah", 8, 0.30),
            ("Sedih", 7, 0.45), ("Bosan", 5, 0.50), ("Antusias", 3, 0.90), ("Frustrasi", 2, 0.35)]
REGIONS = ["Jakarta", "Surabaya", "Bandung", "Yogyakarta", "Bali", "Medan", "Makassar", 
           "Desa Jawa", "Desa Sumatera", "Papua"]

def generate_persona():
    gender = random.choices([g[0] for g in GENDERS], [g[1] for g in GENDERS])[0]
    age = random.choices([a[0] for a in AGES], [a[1] for a in AGES])[0]
    social = random.choices([s[0] for s in SOCIAL], [s[1] for s in SOCIAL])[0]
    emotion = random.choices([e[0] for e in EMOTIONS], [e[1] for e in EMOTIONS])[0]
    emotion_acc = next(e[2] for e in EMOTIONS if e[0] == emotion)
    region = random.choice(REGIONS)
    
    # Adjust accuracy
    if age == "Anak":
        emotion_acc *= 0.7
    elif age == "Lansia":
        emotion_acc *= 0.9
    
    is_correct = random.random() < emotion_acc
    feedback = 1 if is_correct else 0
    
    return {
        'gender': gender, 'age': age, 'social': social, 'emotion': emotion,
        'region': region, 'feedback': feedback, 'accuracy': emotion_acc
    }

def main():
    target = 1_000_000
    batch_size = 10000
    
    print("="*70)
    print(f"  MEGA FAST - {target:,} Interaksi")
    print("="*70)
    
    conn = sqlite3.connect('logs/feedback/self_improve.db')
    cursor = conn.cursor()
    
    # Get current count
    cursor.execute("SELECT COUNT(*) FROM interactions")
    start_count = cursor.fetchone()[0]
    print(f"  Starting count: {start_count:,}")
    print(f"  Target: {target:,}")
    print(f"  Batch size: {batch_size:,}")
    print("="*70)
    
    start_time = datetime.now()
    inserted = 0
    
    for batch in range(target // batch_size):
        batch_data = []
        for i in range(batch_size):
            p = generate_persona()
            ts = (datetime.now() - timedelta(minutes=random.randint(0, 10080))).isoformat()
            
            batch_data.append((
                ts,
                f"mega_{p['region']}_{batch*batch_size+i}",
                json.dumps({'demo': p}),
                json.dumps({'pred': random.randint(0, 1)}),
                'best_model_logistic_regression',
                p['feedback'],
                f"{p['emotion']}_{p['social']}",
                random.uniform(50, 500),
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
            remaining = (target - inserted) / rate if rate > 0 else 0
            print(f"  Progress: {inserted:,}/{target:,} | Rate: {rate:.0f}/s | ETA: {remaining/60:.0f}m")
    
    # Final
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
