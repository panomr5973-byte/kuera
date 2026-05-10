# 🤖 KUWERA Admin Panel

Advanced AI Administration Dashboard dengan 3D Avatar Interaktif

## 🎯 Features

### Core Features
- **3D Avatar Interaktif** - Three.js powered AI face dengan animasi real-time
- **Dashboard Monitoring** - Real-time stats dan metrics
- **Model Registry** - Lihat dan manage semua model AI
- **Interaction Logs** - Track user interactions (chat, voice, API)
- **Dual-Drive Manager** - Visualisasi path C: dan D:
- **Sync Status** - Monitor backup dan sinkronisasi
- **Evolution Timeline** - Track perkembangan AI dari waktu ke waktu
- **System History** - Log semua aktivitas sistem

### 3D Avatar Capabilities
- **Eye Tracking** - Mata mengikuti cursor mouse
- **Blink Animation** - Animasi berkedip natural
- **Mouth Animation** - Animasi bicara saat chat
- **Holographic Rings** - Visual efek futuristik
- **Neural Circuit** - Detail teknis pada kepala
- **Particle System** - Partikel floating effect

## 🚀 Quick Start

### Run Admin Panel
```bash
cd C:\AI-Project\admin_panel
python start_admin.py
```

Atau langsung:
```bash
python admin_panel\start_admin.py
```

Server akan berjalan di `http://localhost:5000`

### Manual Start (Windows)
Double-click: `start_admin_panel.bat`

## 📁 Structure

```
admin_panel/
├── api/
│   └── server.py          # Flask backend API
├── static/
│   ├── css/
│   │   └── admin-panel.css # Styling futuristik
│   ├── js/
│   │   ├── avatar-3d.js    # Three.js avatar controller
│   │   └── admin-panel.js  # Main app logic
│   └── assets/             # Images, models, textures
├── templates/
│   └── index.html          # Main dashboard
├── start_admin.py          # Launcher script
└── README.md               # This file
```

## 🎮 Using the 3D Avatar

### Chat dengan Avatar
1. Klik panel chat di sebelah kanan avatar
2. Ketik pesan dan tekan Enter atau tombol send
3. Avatar akan merespons dengan animasi bicara

### Controls
- **SPEAK** - Trigger avatar speech dengan sample text
- **LISTEN** - Aktifkan mode listening (visual feedback)
- **ANIMATE** - Trigger special animation sequence

### Interaktivitas
- Gerakkan mouse untuk eye tracking
- Avatar akan berkedip secara natural
- Holographic rings berputar terus-menerus
- Particle system bergerak mengikuti waktu

## 📊 Dashboard Panels

### 1. Dashboard (Utama)
- 3D Avatar dengan chat interface
- Quick stats (models, interactions, accuracy, space)
- Evolution chart dan interaction distribution
- Quick actions (sync, retrain, backup, clean)

### 2. Evolution
- Timeline evolusi AI dari Genesis sampai sekarang
- Stats: Current Generation, Evolution Score, F1 Trend

### 3. Models
- Grid view semua model
- Production model badge
- Metrics: F1 Score, Accuracy, Samples, Date

### 4. Interactions
- Filter by type: All, Chat, Voice, API
- Real-time interaction log
- User info dan timestamp

### 5. Path Manager
- Visualisasi dual-drive (C: dan D:)
- Usage bars untuk setiap drive
- List semua important paths

### 6. Sync Status
- Last sync timestamp
- Sync statistics
- Sync history log

### 7. Roadmap
- Timeline pengembangan future
- Phase: Inception → Toddler → Adolescent → Nusantara → Bhineka → Pancasila

### 8. History
- System event log
- Filter by date dan type
- Detail setiap event

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Dashboard statistics |
| `/api/models` | GET | List all models |
| `/api/models/<id>` | GET | Get specific model |
| `/api/interactions` | GET | Get interactions |
| `/api/sync/status` | GET | Sync status |
| `/api/system/status` | GET | System & disk status |
| `/api/paths` | GET | Path configuration |
| `/api/evolution/timeline` | GET | Evolution phases |
| `/api/history` | GET | System history |
| `/api/chat` | POST | Send chat message |
| `/api/sync/trigger` | POST | Trigger manual sync |
| `/api/retrain` | POST | Trigger model retrain |

## 🎨 Customization

### Change Avatar Colors
Edit `static/js/avatar-3d.js`:
```javascript
this.eyeMaterial = new THREE.MeshPhongMaterial({
    color: 0x00d4ff,  // Change eye color
    emissive: 0x00d4ff,
    emissiveIntensity: 0.8
});
```

### Change Theme Colors
Edit `static/css/admin-panel.css`:
```css
:root {
    --primary: #00d4ff;    /* Main accent */
    --secondary: #7b2dff;  /* Secondary accent */
    --success: #00ff88;    /* Success state */
    /* ... */
}
```

## 🔧 Troubleshooting

### Avatar tidak muncul
- Pastikan browser mendukung WebGL
- Cek console untuk error Three.js
- Refresh page (F5)

### API tidak merespons
- Pastikan port 5000 tidak digunakan
- Cek firewall settings
- Restart server dengan `start_admin.py`

### Style tidak load
- Clear browser cache (Ctrl+Shift+R)
- Pastikan path static files benar

## 📱 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

**Note**: WebGL harus di-enable untuk 3D avatar

## 🔮 Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Voice recognition integration
- [ ] Advanced facial expressions
- [ ] VR/AR support
- [ ] Mobile app companion
- [ ] AI-powered insights

---

**KUWERA Admin Panel v1.0**  
Built with ❤️ for Indonesian AI Evolution
