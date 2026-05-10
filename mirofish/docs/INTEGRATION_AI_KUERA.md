# 🤖 Integrasi Mirofish AI dengan AI Kuera

Dokumen ini menjelaskan cara mengintegrasikan Mirofish AI (Smart Aquaculture) dengan sistem AI Kuera yang sudah ada.

## 📋 Overview

Integrasi ini memungkinkan:
1. **AI Kuera** mengakses data sensor dari Mirofish
2. **Mirofish** menggunakan model AI dari AI Kuera untuk prediksi
3. **Chat Interface** untuk tanya jawab tentang kondisi kolam
4. **Rekomendasi pintar** berbasis data real-time

## 🔌 Arsitektur Integrasi

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI KUERA (Existing)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   LLM Models│  │  Knowledge  │  │   Chat API  │             │
│  │   (12 GGUF) │  │   Graph     │  │             │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          │                                       │
│                   ┌──────▼──────┐                               │
│                   │  AI Engine  │                               │
│                   └──────┬──────┘                               │
└──────────────────────────┼──────────────────────────────────────┘
                           │ REST API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MIROFISH AI (New)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Sensors   │  │  Analytics  │  │  Dashboard  │             │
│  │   (Sim/Real)│  │   Engine    │  │  (Streamlit)│             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    Alert    │  │  Prediction │  │    Chat     │             │
│  │   System    │  │    API      │  │  Interface  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## ⚙️ Setup Integrasi

### 1. Konfigurasi Environment

Edit file `mirofish/backend/.env`:

```env
# AI Kuera Integration
KUERA_INTEGRATION_ENABLED=true
KUERA_API_URL=http://localhost:8000  # URL AI Kuera API
KUERA_API_KEY=your-api-key-here       # Jika menggunakan auth

# Mirofish Settings
MIROFISH_API_URL=http://localhost:8001  # URL Mirofish API
MIROFISH_DATA_SYNC_INTERVAL=300         # Sync setiap 5 menit
```

### 2. Jalankan Kedua Sistem

**Terminal 1 - AI Kuera**:
```bash
cd D:\workspace\AI-Project
# Jalankan AI Kuera (jika ada commandnya)
# atau pastikan API Kuera berjalan di port 8000
```

**Terminal 2 - Mirofish Backend**:
```bash
cd D:\workspace\AI-Project\mirofish\backend
python main.py
```

**Terminal 3 - Mirofish Frontend**:
```bash
cd D:\workspace\AI-Project\mirofish\frontend
streamlit run app.py
```

## 🔗 API Integration Points

### 1. Mirofish → AI Kuera (Data Push)

Mirofish mengirim data sensor ke AI Kuera untuk analisis.

```python
# mirofish/backend/app/services/ai_kuera_integration.py

import httpx
from datetime import datetime
from typing import Dict, List

class AIKueraIntegration:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_sensor_data(self, pond_id: str, readings: Dict):
        """Send sensor data to AI Kuera."""
        payload = {
            "source": "mirofish",
            "pond_id": pond_id,
            "timestamp": datetime.utcnow().isoformat(),
            "readings": readings
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/external/mirofish/data",
                json=payload
            )
            return response.json()
        except Exception as e:
            print(f"Error sending data to AI Kuera: {e}")
            return None
    
    async def get_recommendations(self, pond_id: str, current_data: Dict):
        """Get AI recommendations for pond conditions."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/ai/recommendations",
                json={
                    "pond_id": pond_id,
                    "data": current_data,
                    "context": "aquaculture"
                }
            )
            return response.json()
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return None
    
    async def query_chat(self, query: str, pond_id: str = None):
        """Query AI Kuera chatbot about pond conditions."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/chat",
                json={
                    "message": query,
                    "pond_id": pond_id,
                    "source": "mirofish"
                }
            )
            return response.json()
        except Exception as e:
            print(f"Error querying chat: {e}")
            return None
```

### 2. AI Kuera → Mirofish (Query Data)

AI Kuera dapat mengambil data dari Mirofish untuk analisis.

```python
# Endpoint di Mirofish untuk melayani request dari AI Kuera

@router.get("/api/v1/external/data/{pond_id}")
async def get_pond_data_for_external(
    pond_id: str,
    hours: int = 24,
    api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get pond data for external systems (AI Kuera)."""
    # Validate API key
    validate_api_key(api_key)
    
    # Get readings
    from_date = datetime.utcnow() - timedelta(hours=hours)
    readings = db.query(SensorReading).filter(
        SensorReading.pond_id == pond_id,
        SensorReading.recorded_at >= from_date
    ).all()
    
    # Get pond info
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    
    return {
        "pond": {
            "id": pond.id,
            "name": pond.name,
            "fish_type": pond.fish_type,
            "fish_count": pond.fish_count
        },
        "readings": [
            {
                "sensor_type": r.sensor.type.value if r.sensor else None,
                "value": r.value,
                "unit": r.unit,
                "timestamp": r.recorded_at.isoformat()
            }
            for r in readings
        ],
        "summary": generate_summary(readings)
    }
```

## 🤖 Use Cases Integrasi

### Use Case 1: Rekomendasi Pintar

**Scenario**: pH kolam turun ke 6.2 (di bawah threshold)

**Flow**:
1. Mirofish detect pH rendah → Create Alert
2. Mirofish send data ke AI Kuera
3. AI Kuera analyze dan generate rekomendasi
4. Mirofish display rekomendasi di dashboard

```python
# Implementasi di Alert Service
async def process_alert_with_ai(alert_id: str):
    alert = get_alert(alert_id)
    pond_data = get_pond_latest_data(alert.pond_id)
    
    # Get AI recommendation
    ai_response = await ai_kuera.get_recommendations(
        pond_id=alert.pond_id,
        current_data=pond_data
    )
    
    # Update alert with recommendation
    alert.ai_recommendation = ai_response.get("recommendation")
    alert.save()
```

### Use Case 2: Chatbot Aquaculture

**Scenario**: Petani bertanya "Bagaimana kondisi kolam saya?"

**Flow**:
1. User type query di Mirofish chat interface
2. Mirofish fetch data terkini
3. Mirofish send query + data ke AI Kuera
4. AI Kuera generate response berbasis data real
5. Display response ke user

```python
# Chat handler
async def handle_chat_query(query: str, pond_id: str = None):
    # Get context data
    context = {}
    if pond_id:
        context["pond_data"] = get_pond_latest_data(pond_id)
        context["alerts"] = get_active_alerts(pond_id)
    
    # Query AI Kuera
    response = await ai_kuera.query_chat(
        query=query,
        context=context
    )
    
    return response.get("message")
```

### Use Case 3: Prediksi Kondisi

**Scenario**: Prediksi kondisi kolam 24 jam ke depan

**Flow**:
1. Mirofish collect historical data (7 days)
2. Send ke AI Kuera prediction endpoint
3. AI Kuera run forecasting model
4. Return prediction ke Mirofish
5. Display prediction chart di dashboard

```python
# Prediction service
async def get_prediction(pond_id: str, hours_ahead: int = 24):
    # Get historical data
    history = get_historical_data(pond_id, days=7)
    
    # Call AI Kuera prediction
    prediction = await ai_kuera.predict(
        pond_id=pond_id,
        historical_data=history,
        forecast_hours=hours_ahead
    )
    
    return prediction
```

## 📊 Data Format

### Sensor Data Format

```json
{
  "source": "mirofish",
  "pond_id": "uuid-pond-123",
  "timestamp": "2026-01-15T10:30:00Z",
  "readings": {
    "ph": {
      "value": 7.2,
      "unit": "pH",
      "status": "normal"
    },
    "dissolved_o2": {
      "value": 6.5,
      "unit": "mg/L",
      "status": "normal"
    },
    "temperature": {
      "value": 26.5,
      "unit": "°C",
      "status": "normal"
    }
  },
  "farm_info": {
    "farm_id": "uuid-farm-456",
    "location": "Jakarta, Indonesia",
    "fish_type": "Tilapia"
  }
}
```

### AI Recommendation Format

```json
{
  "pond_id": "uuid-pond-123",
  "timestamp": "2026-01-15T10:30:00Z",
  "recommendations": [
    {
      "priority": "high",
      "parameter": "ph",
      "current_value": 6.2,
      "target_value": 7.0,
      "action": "Tambahkan kapur (dolomite) sebanyak 50-100 gram per m³",
      "reasoning": "pH di bawah optimal untuk ikan nila (6.5-8.5)",
      "timeline": "Segera"
    }
  ],
  "predictions": {
    "next_24h": {
      "ph_trend": "stable",
      "do_trend": "decreasing",
      "risk_level": "medium"
    }
  }
}
```

## 🔒 Security

### API Key Authentication

```python
# Middleware untuk validasi API key
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("MIROFISH_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/external/data/{pond_id}")
@limiter.limit("100/hour")  # Max 100 requests per hour
async def get_external_data(...):
    ...
```

## 🧪 Testing Integrasi

### Test Script

```python
# test_integration.py
import httpx
import asyncio

async def test_integration():
    # Test Mirofish → AI Kuera
    async with httpx.AsyncClient() as client:
        # Send sensor data
        response = await client.post(
            "http://localhost:8000/api/v1/external/mirofish/data",
            json={
                "pond_id": "test-pond",
                "readings": {"ph": 6.2, "do": 5.5}
            }
        )
        print(f"Data push: {response.status_code}")
        
        # Get recommendations
        response = await client.post(
            "http://localhost:8000/api/v1/ai/recommendations",
            json={"pond_id": "test-pond"}
        )
        print(f"Recommendations: {response.json()}")

if __name__ == "__main__":
    asyncio.run(test_integration())
```

## 📈 Monitoring Integrasi

### Health Check Endpoint

```python
@router.get("/api/v1/integration/health")
async def integration_health():
    """Check health of AI Kuera integration."""
    try:
        # Ping AI Kuera
        response = httpx.get(f"{AI_KUERA_URL}/health", timeout=5.0)
        ai_kuera_status = "connected" if response.status_code == 200 else "error"
    except:
        ai_kuera_status = "disconnected"
    
    return {
        "mirofish_status": "healthy",
        "ai_kuera_status": ai_kuera_status,
        "last_sync": get_last_sync_time(),
        "pending_syncs": get_pending_sync_count()
    }
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection refused | AI Kuera not running | Start AI Kuera service |
| Timeout | Network slow | Increase timeout in config |
| Auth failed | Invalid API key | Check API key in .env |
| Data not syncing | Sync interval too long | Reduce sync interval |

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Di Mirofish backend
DEBUG=true python main.py
```

## 📝 TODO Integrasi

- [ ] Implementasi AI Kuera client
- [ ] Setup webhook untuk real-time sync
- [ ] Chat interface di Streamlit
- [ ] Automated recommendation system
- [ ] Prediction model integration
- [ ] Alert correlation
- [ ] Data visualization integration

---

**Catatan**: Dokumen ini akan diupdate seiring implementasi integrasi berjalan.
