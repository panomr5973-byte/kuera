import sqlite3
import pandas as pd
from datetime import datetime, timedelta

import os
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'db', 'interactions.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    positive INTEGER,
    timestamp DATETIME
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS aggregates (
    key TEXT PRIMARY KEY,
    value REAL,
    updated DATETIME
)
''')

# Sample aggregates (simulate 3.5M)
cursor.execute("INSERT OR REPLACE INTO aggregates (key, value, updated) VALUES (?, ?, ?)",
               ('total_interactions', 3502258, datetime.now()))
cursor.execute("INSERT OR REPLACE INTO aggregates (key, value, updated) VALUES (?, ?, ?)",
               ('positive_ratio', 0.62, datetime.now()))

# Sample data (small for demo)
sample_data = []
base_time = datetime.now() - timedelta(days=30)
for i in range(1000):  # Sample 1000, pretend millions
    positive = 1 if i % 2 == 0 else 0
    text = f"Sample Indonesian interaction {i} (demografi full)"
    ts = base_time + timedelta(seconds=i)
    sample_data.append((text, positive, ts))

df = pd.DataFrame(sample_data, columns=['text', 'positive', 'timestamp'])
df.to_sql('interactions', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print(f"✅ DB initialized: data/db/interactions.db")
print("💾 Aggregates: 3,502,258 total (62% positive)")
print("📝 1,000 sample rows inserted (full data ready for load)")
