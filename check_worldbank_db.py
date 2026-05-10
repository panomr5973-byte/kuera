#!/usr/bin/env python
"""Check World Bank Database"""
import sqlite3

conn = sqlite3.connect('data/worldbank_indonesia.db')
cursor = conn.cursor()

print("="*70)
print("KUWERA WORLDBANK DATABASE CHECK")
print("="*70)

# Cek tabel
print("\n[Tables]")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for table in cursor.fetchall():
    print(f"  - {table[0]}")

# Hitung data
cursor.execute("SELECT COUNT(*) FROM worldbank_indicators")
count = cursor.fetchone()[0]
print(f"\n[Total Records: {count}]")

# Sample data terbaru
print("\n[Latest Data Sample]")
cursor.execute('''
    SELECT indicator_name, year, value, category 
    FROM worldbank_indicators 
    ORDER BY year DESC, category 
    LIMIT 10
''')
print("-" * 70)
print(f"{'Indikator':<40} | Tahun | Nilai")
print("-" * 70)
for row in cursor.fetchall():
    print(f"{row[0][:38]:<40} | {row[1]} | {row[2]:>12,.2f}")

conn.close()
print("-" * 70)
print("\n[OK] Database aktif dan siap digunakan!")
print("\nCara menggunakan:")
print("  1. python kuera_worldbank_chat.py    # Chat dengan AI")
print("  2. python kuera_worldbank_trainer.py # Retrain model")
print("="*70)
