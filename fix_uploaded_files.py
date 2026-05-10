#!/usr/bin/env python
"""Fix uploaded files that have error content"""

from kuera_setup_database import KueraDatabase

db = KueraDatabase()
db.connect()

# Delete files with error content
db.cursor.execute("DELETE FROM uploaded_files WHERE content_text LIKE '%PyPDF2 not installed%'")
deleted_files = db.cursor.rowcount

# Delete all chunks
db.cursor.execute('DELETE FROM knowledge_chunks')

db.conn.commit()
db.close()

print(f'[OK] Deleted {deleted_files} corrupted file(s)')
print('[INFO] Please re-upload your PDF file to KUERA!')
