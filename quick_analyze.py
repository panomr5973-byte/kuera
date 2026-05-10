import sqlite3
import json
from collections import Counter

conn = sqlite3.connect('logs/feedback/self_improve.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT user_input, user_feedback 
    FROM interactions 
    WHERE session_id LIKE 'kalimantan_%'
""")

data = cursor.fetchall()

provinsi = Counter()
gender = Counter()
umur = Counter()
pekerjaan = Counter()
pendidikan = Counter()
ekonomi = Counter()
etnis = Counter()
emosi = Counter()

for row in data:
    try:
        persona = json.loads(row[0])
        provinsi[persona.get('provinsi')] += 1
        gender[persona.get('gender')] += 1
        umur[persona.get('umur')] += 1
        pekerjaan[persona.get('pekerjaan')] += 1
        pendidikan[persona.get('pendidikan')] += 1
        ekonomi[persona.get('ekonomi')] += 1
        etnis[persona.get('etnis')] += 1
        emosi[persona.get('emosi')] += 1
    except:
        pass

print('='*60)
print('ANALISIS DATA KALIMANTAN - BPS')
print('='*60)
print(f'\nTotal: {len(data):,} interaksi')

print('\n[PROVINSI]')
for prov, count in provinsi.most_common():
    print(f'  {prov}: {count:,} ({count/len(data)*100:.1f}%)')

print('\n[GENDER]')
for g, count in gender.most_common():
    print(f'  {g}: {count:,} ({count/len(data)*100:.1f}%)')

print('\n[UMUR]')
for u, count in umur.most_common():
    print(f'  {u}: {count:,} ({count/len(data)*100:.1f}%)')

print('\n[PEKERJAAN TOP 5]')
for job, count in pekerjaan.most_common(5):
    print(f'  {job}: {count:,}')

print('\n[ETNIS]')
for eth, count in etnis.most_common():
    print(f'  {eth}: {count:,} ({count/len(data)*100:.1f}%)')

print('\n[EKONOMI]')
for econ, count in ekonomi.most_common():
    print(f'  {econ}: {count:,}')

print('\n[EMOSI TOP 5]')
for em, count in emosi.most_common(5):
    print(f'  {em}: {count:,}')

conn.close()
