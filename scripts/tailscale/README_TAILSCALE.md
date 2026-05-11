# 🌐 Tailscale Integration - KUERA Network

Tailnet: `panomr5973@gmail.com` | 3 machines connected

## Your Tailnet

| Machine | Tailscale IP | Platform | Role | Status |
|---------|-------------|----------|------|--------|
| **kuera-vps** | `100.111.193.44` | Ubuntu 22.04 (Vultr) | Exit Node, Reverse Proxy, Ollama | ✅ Active |
| **WORKSTATION-LOCAL** | `192.168.1.100` | Windows 11 25H2 | Workstation, KUERA Desktop | ✅ Active |
| **v2201** | `100.99.229.51` | Android 14 | Mobile | 💤 Offline (last seen 7m) |

---

## ✅ What's Already Working

### 1. Nginx Reverse Proxy (VPS)
- **Port**: `9090` on VPS (`100.111.193.44:9090`)
- **Proxy to**: Windows KUERA services via Tailscale
- **Routes**:
  - `/` → KUERA Control Panel (Windows:7777)
  - `/api/` → KUERA API (Windows:8000)
  - `/real-api/` → Real API (Windows:8001)
  - `/web/` → Web v2 (Windows:5000)
  - `/admin/` → Admin Panel (Windows:5001)
  - `/dashboard/` → Streamlit Dashboard (Windows:8501)
  - `/nginx-health` → Nginx health check

**Test from any device in tailnet:**
```bash
curl http://100.111.193.44:9090/nginx-health
# → "nginx OK"
```

### 2. Ollama on VPS
- **Port**: `11434` on VPS
- Ollama is running on the VPS — can serve as centralized LLM backend
- Access from Windows: `curl http://100.111.193.44:11434/api/tags`

### 3. Tailscale Connectivity
- All devices can reach each other via Tailscale IPs
- Windows → VPS ping: ~24-61ms
- SSH via Tailscale IP works (when authorized)

---

## ⏳ What You Need to Enable Manually

### A. Tailscale SSH (for passwordless VPS access)

**Status**: Waiting for authorization

**What to do:**
1. Visit: https://login.tailscale.com/a/ld547058358af5
2. Click **Authorize**
3. Done! You can then SSH to VPS without password:
   ```bash
   ssh root@100.111.193.44
   ```

### B. Tailscale Funnel (expose KUERA to the internet)

**Status**: Not enabled on tailnet

**What to do:**
1. Visit: https://login.tailscale.com/f/funnel?node=nuyBxkS1Wk11CNTRL
2. Click **Enable Funnel**
3. Then on VPS, run:
   ```bash
   tailscale funnel --bg 9090
   ```
4. You will get a public URL like:
   ```
   https://kuera-vps.your-tailnet.ts.net/
   ```
5. Anyone can access KUERA from anywhere via that URL!

### C. Tailscale Serve (private access within tailnet)

**Status**: Not enabled on tailnet

**What to do:**
1. Visit: https://login.tailscale.com/f/serve?node=nuyBxkS1Wk11CNTRL
2. Click **Enable Serve**
3. Then on VPS, run:
   ```bash
   tailscale serve --bg 9090
   ```
4. Access KUERA from any tailnet device via:
   ```
   https://kuera-vps.your-tailnet.ts.net/
   ```
   (No public internet access — only your devices)

---

## 🚀 PowerShell Manager (Windows)

Use `kuera_tailscale.ps1` from this folder:

```powershell
# Check all tailnet connectivity
.\kuera_tailscale.ps1 -Action status

# Test KUERA via VPS reverse proxy
.\kuera_tailscale.ps1 -Action test-proxy

# Test Ollama on VPS
.\kuera_tailscale.ps1 -Action test-ollama

# Quick SSH to VPS (after Tailscale SSH enabled)
.\kuera_tailscale.ps1 -Action ssh

# Show all tailnet machines
.\kuera_tailscale.ps1 -Action machines
```

---

## 🔒 Security Notes

- Tailscale creates an encrypted mesh VPN — traffic never touches the public internet
- Funnel exposes **only** port 9090 (nginx) to the public
- Nginx only proxies to Windows services — VPS itself has no direct access
- Enable HTTPS in Tailscale dashboard for encrypted public access

---

## 📋 Next Steps

1. **Enable Tailscale SSH** → Visit auth URL above
2. **Test**: `ssh root@100.111.193.44` from Windows
3. **Enable Funnel or Serve** → Visit enable URL above
4. **Run funnel**: `tailscale funnel --bg 9090` on VPS
5. **Access KUERA** from anywhere!
