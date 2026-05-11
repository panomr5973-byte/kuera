# 🎛️ KUWERA Admin Panel - Complete Setup Guide

## 🚀 LAUNCHING THE ADMIN PANEL

### Method 1: Batch File (Recommended)
```
Double-click: C:\AI-Project\start_admin_panel.bat
```

### Method 2: Python Script
```bash
cd C:\AI-Project
python admin_panel\start_admin.py
```

### Method 3: Manual Flask
```bash
cd C:\AI-Project\admin_panel\api
python server.py
```

## 📱 ACCESSING THE PANEL

Once started, open browser:
```
http://localhost:5000
```

The panel will open automatically after 2 seconds.

---

## 🎯 FEATURE HIGHLIGHTS

### 1. Interactive 3D Avatar
Located at the top-left of dashboard
- **Eye Tracking**: Move mouse to see avatar follow
- **Chat Interface**: Type messages in the chat box
- **Voice Animation**: Avatar mouth moves when "speaking"
- **Blinking**: Natural random blinking
- **Holographic Effects**: Rotating rings and particles

**Controls:**
- 🎤 **SPEAK** - Avatar speaks sample text
- 👂 **LISTEN** - Visual feedback mode
- 🎭 **ANIMATE** - Special animation

### 2. Dashboard Stats
Real-time monitoring:
- Active Models: 6
- Total Interactions: 1,002,258+
- Best Accuracy: 67.3%
- Free Space: 67.9 GB

### 3. Evolution Timeline
Track AI development phases:
```
Inception → Toddler → Adolescent → Nusantara → Bhineka → Pancasila
```

### 4. Model Registry
View all 6 models dengan metrics:
- F1 Score
- Accuracy  
- Training Samples
- Production status

### 5. Dual-Drive Visualizer
See C: dan D: drive status:
- Space usage bars
- Path listings
- Sync status

### 6. System History
Complete event log:
- Model creations
- Sync events
- System errors
- Maintenance logs

---

## 🎮 USING THE AVATAR

### Example Conversation
1. Click chat input box
2. Type: "Halo KUWERA"
3. Press Enter
4. Avatar will respond dengan animasi

### Available Commands (Type in chat)
- "status" - Get system status
- "models" - List models
- "sync" - Trigger sync
- "help" - Show help

---

## 🔧 ADMIN ACTIONS

### Quick Actions Panel
Located di dashboard bawah:

1. **⟲ Sync Models**
   - Manual sync C: → D:
   - Updates backup

2. **⚡ Retrain Model**
   - Trigger retraining
   - Creates new generation

3. **💾 Backup Data**
   - Full backup to D:
   - Includes logs & configs

4. **🧹 Clean Logs**
   - Remove old logs (>30 days)
   - Archive to D:

---

## 📊 PANEL NAVIGATION

### Sidebar Menu
```
MAIN
├── Dashboard      - Overview & Avatar
├── Evolution      - Development timeline
├── Models         - Model registry
└── Interactions   - User activity log

SYSTEM
├── Path Manager   - C: & D: visualizer
├── Sync Status    - Backup monitoring
├── Roadmap        - Future plans
└── History        - Event logs
```

---

## 🔌 API INTEGRATION

### Fetch Stats
```javascript
fetch('http://localhost:5000/api/stats')
  .then(r => r.json())
  .then(data => console.log(data))
```

### Send Chat
```javascript
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: "Hello"})
})
```

### Trigger Sync
```javascript
fetch('http://localhost:5000/api/sync/trigger', {
  method: 'POST'
})
```

---

## 🎨 CUSTOMIZATION

### Change Colors
Edit `admin_panel/static/css/admin-panel.css`:
```css
:root {
  --primary: #00d4ff;    /* Cyan - Main accent */
  --secondary: #7b2dff;  /* Purple */
  --success: #00ff88;    /* Green */
  --accent: #ff2d7b;     /* Pink */
}
```

### Change Avatar Appearance
Edit `admin_panel/static/js/avatar-3d.js`:
```javascript
// Eye color
this.eyeMaterial = new THREE.MeshPhongMaterial({
    color: 0x00d4ff,  // Change this
    emissive: 0x00d4ff
});
```

---

## 🐛 TROUBLESHOOTING

### Avatar Not Showing (Black Box)
**Cause**: WebGL not supported
**Fix**: 
- Update browser
- Enable hardware acceleration
- Try Chrome/Firefox

### "Cannot Connect to Server"
**Cause**: Port 5000 in use
**Fix**:
```bash
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill process or change port in server.py
```

### Styles Not Loading
**Fix**: Hard refresh browser
```
Ctrl + Shift + R
```

### API Errors
**Check**:
1. Server running?
2. Python Flask installed?
3. CORS enabled?

---

## 📈 PERFORMANCE TIPS

### Optimizing 3D Avatar
If laggy, reduce:
```javascript
// In avatar-3d.js, reduce particle count
const particleCount = 50; // Change to 25

// Reduce geometry detail
const headGeometry = new THREE.SphereGeometry(1, 16, 16); // was 32,32
```

### Disabling Animations
For low-end systems:
```javascript
// Comment out in animate() loop
// this.particleSystem.rotation.y += 0.001;
```

---

## 🔒 SECURITY NOTES

### Default Configuration
- Server runs on localhost only
- No authentication (add if needed)
- Debug mode enabled (disable in production)

### Production Deployment
1. Disable debug mode:
```python
app.run(debug=False)
```

2. Add authentication:
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
```

3. Use HTTPS
4. Set strong secret key

---

## 🎯 NEXT STEPS

After setup:
1. ✅ Explore all 8 panels
2. ✅ Chat dengan 3D Avatar
3. ✅ Check Evolution timeline
4. ✅ Review Model registry
5. ✅ Monitor disk space
6. ✅ Test sync functionality

### Future Enhancements
- [ ] Voice recognition
- [ ] Mobile responsive
- [ ] Dark/Light theme toggle
- [ ] Real-time notifications
- [ ] Advanced analytics

---

## 📞 SUPPORT

If issues persist:
1. Check browser console (F12)
2. Review server logs
3. Verify file paths
4. Restart server

**Happy Monitoring!** 🤖✨
