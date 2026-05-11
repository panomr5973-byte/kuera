# KUERA Web Interface

## Status Server

```json
{
  "status": "healthy",
  "database_connected": true,
  "rag_available": true,
  "timestamp": "2026-04-02T13:09:20"
}
```

---

## Cara Akses

### 1. Buka Browser
```
http://localhost:5000
```

### 2. API Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/` | GET | Web interface (HTML) |
| `/api/chat` | POST | Kirim pesan chat |
| `/api/stats` | GET | Statistik server & database |
| `/api/health` | GET | Health check |
| `/api/session/<id>` | GET | Info session |

### 3. Contoh API Call

```bash
# Health check
curl http://localhost:5000/api/health

# Chat
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "halo", "session_id": "abc123"}'

# Stats
curl http://localhost:5000/api/stats
```

---

## Fitur Web Interface

### Chat Interface
- Real-time chat dengan KUERA
- Intent recognition (halo, siapa kamu, apa itu kuera, dll)
- Session management
- Auto-save ke database

### Dashboard
- **Server Status**: Database connection, API status, Uptime
- **Database Info**: Path, Size (~2.5 GB), Records (3.5M+)
- **Quick Actions**: Tombol cepat untuk pertanyaan umum
- **Statistics**: Total interaksi, sessions, confidence

### Quick Actions
- "Siapa kamu?"
- "Apa itu KUERA?"
- "Bisa apa?"
- "Tentang Indonesia"
- "Statistik DB"
- "Bantuan"

---

## Database Connection

```
Path:    data/kuera_database.db
Size:    2.5 GB
Records: 3,502,258+ interactions
Tables:  interactions, user_profiles, model_metrics, sessions
Status:  Connected ✓
```

---

## Koneksi Server

```
Host:    0.0.0.0
Port:    5000
URL:     http://localhost:5000
Status:  Running ✓
```

---

## Troubleshooting

### Server tidak berjalan?
```bash
python kuera_web_server.py
```

### Port 5000 busy?
Edit file `kuera_web_server.py` dan ganti port:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Database error?
Pastikan file `data/kuera_database.db` ada:
```bash
ls -lh data/*.db
```

---

## Screenshot Expected

```
┌─────────────────────────────────────────────────────────────────┐
│  KUERA - Kumpulan Era Rakyat                                    │
│  AI Indonesia dari Sabang sampai Merauke                        │
│  [3.5M Interaksi] [34 Provinsi] [34% Avg Conf]                  │
├────────────────────────────────┬────────────────────────────────┤
│                                │  Server Status                 │
│  💬 Chat dengan KUERA          │  • Database: Connected ✓       │
│                                │  • API: Online ✓               │
│  [Chat messages here...]       │  • Uptime: 00:05:23            │
│                                │                                │
│  [Ketik pesan...] [Kirim]      │  Database Info                 │
│                                │  • Path: data/kuera.db         │
│                                │  • Size: ~2.5 GB               │
│                                │  • Records: 3.5M+              │
│                                │                                │
│                                │  Quick Actions                 │
│                                │  [Siapa kamu?] [Apa KUERA?]    │
│                                │  [Bisa apa?]   [Indonesia]     │
└────────────────────────────────┴────────────────────────────────┘
```

---

**Buka http://localhost:5000 di browser Anda sekarang!** 🚀
