# 🐟 Mirofish AI - Smart Aquaculture System

**Mirofish AI** adalah sistem monitoring budidaya perikanan pintar berbasis IoT dan AI yang dirancang untuk membantu petani ikan memantau kualitas air dan kondisi kolam secara real-time.

## ✨ Features

- **📊 Real-time Monitoring**: Pantau pH, DO, suhu, dan parameter lainnya
- **🚨 Smart Alerts**: Notifikasi otomatis ketika parameter di luar batas aman
- **📈 Analytics**: Analisis tren dan prediksi kondisi kolam
- **🎮 Sensor Simulation**: Uji sistem tanpa hardware fisik
- **🤖 AI Integration**: Terintegrasi dengan AI Kuera untuk rekomendasi pintar
- **📱 Responsive UI**: Dashboard modern dengan Streamlit
- **🔄 REST API**: API lengkap untuk integrasi dengan sistem lain

## 🏗️ Architecture

```
Mirofish AI/
├── backend/           # FastAPI Backend
│   ├── app/
│   │   ├── api/      # API Endpoints
│   │   ├── core/     # Configuration
│   │   ├── models/   # Database Models
│   │   └── services/ # Business Logic
│   └── main.py       # Entry Point
├── frontend/         # Streamlit Frontend
│   └── app.py        # Dashboard UI
├── database/         # SQLite Database
├── docs/             # Documentation
└── README.md
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Frontend | Streamlit |
| Database | SQLite |
| Simulation | Python Asyncio |
| Charts | Plotly |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- 4GB RAM minimum (8GB recommended)
- 500MB free storage

### Installation

1. **Clone atau copy repository** ke direktori Anda:
```bash
cd D:\workspace\AI-Project\mirofish
```

2. **Setup Backend**:
```bash
cd backend

# Create virtual environment (opsional tapi direkomendasikan)
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Edit .env sesuai kebutuhan Anda
```

3. **Setup Frontend**:
```bash
cd frontend

# Install dependencies (gunakan venv yang sama atau terpisah)
pip install -r requirements.txt
```

### Running the Application

1. **Start Backend Server**:
```bash
cd backend
python main.py
```
Backend akan berjalan di `http://localhost:8000`

2. **Start Frontend Dashboard** (di terminal baru):
```bash
cd frontend
streamlit run app.py
```
Dashboard akan terbuka di browser `http://localhost:8501`

## 📖 Usage Guide

### 1. Setup Pertama

1. Buka dashboard di browser
2. Buat **Farm** (lokasi budidaya)
3. Buat **Pond** (kolam) dalam farm
4. Inisialisasi **Sensors** untuk pond
5. Start **Simulation** untuk generate data

### 2. Monitoring

- Dashboard menampilkan ringkasan semua pond
- Analytics page untuk detail monitoring
- Alert muncul otomatis jika parameter abnormal

### 3. Thresholds (Default)

| Parameter | Min | Max | Unit |
|-----------|-----|-----|------|
| pH | 6.5 | 8.5 | pH |
| Dissolved O2 | 4.0 | - | mg/L |
| Temperature | 24.0 | 30.0 | °C |
| Ammonia | - | 0.1 | mg/L |

Threshold dapat dikustomisasi per pond.

### 4. Simulation Modes

| Mode | Deskripsi |
|------|-----------|
| Normal | Data dalam range normal |
| Critical | Data di luar threshold (untuk testing alert) |
| Fluctuating | Data dengan variasi tinggi |
| Drifting | Data dengan tren perubahan |

## 🔌 API Documentation

API documentation tersedia di:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

```
GET  /api/v1/farms              # List farms
POST /api/v1/farms              # Create farm
GET  /api/v1/ponds              # List ponds
POST /api/v1/ponds              # Create pond
GET  /api/v1/sensors            # List sensors
POST /api/v1/sensors            # Create sensor
GET  /api/v1/readings/pond/{id} # Get pond readings
GET  /api/v1/alerts             # List alerts
GET  /api/v1/dashboard/summary  # Dashboard summary
```

## 🤖 Integrasi dengan AI Kuera

Mirofish AI dapat terintegrasi dengan AI Kuera untuk:

1. **Rekomendasi Pintar**: AI memberikan saran berdasarkan data sensor
2. **Prediksi**: Prediksi kondisi kolam di masa depan
3. **Analisis**: Analisis mendalam dari data historis
4. **Chatbot**: Tanya jawab tentang kondisi kolam

Untuk mengaktifkan integrasi, edit `.env`:
```env
KUERA_INTEGRATION_ENABLED=true
KUERA_API_URL=http://localhost:8000
```

## 🐳 Docker Deployment (Optional)

```bash
# Build dan run dengan Docker
docker-compose up -d

# Services:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:8501
# - MQTT: localhost:1883
```

## 🔧 Configuration

Konfigurasi via environment variables (`.env`):

```env
# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./database/mirofish.db

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883

# Thresholds
PH_MIN=6.5
PH_MAX=8.5
DO_MIN=4.0
TEMP_MIN=24.0
TEMP_MAX=30.0
AMMONIA_MAX=0.1

# AI Kuera Integration
KUERA_INTEGRATION_ENABLED=true
KUERA_API_URL=http://localhost:8000
```

## 📁 Project Structure

```
mirofish/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   │   ├── farms.py
│   │   │   ├── ponds.py
│   │   │   ├── sensors.py
│   │   │   ├── readings.py
│   │   │   ├── alerts.py
│   │   │   ├── dashboard.py
│   │   │   └── simulation.py
│   │   ├── core/         # Config & utilities
│   │   │   └── config.py
│   │   ├── models/       # Database models
│   │   │   └── database.py
│   │   └── services/     # Business logic
│   │       └── sensor_simulator.py
│   ├── main.py           # FastAPI entry point
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app.py            # Streamlit dashboard
│   └── requirements.txt
├── database/             # SQLite database
└── README.md
```

## 🧪 Testing

```bash
# Run tests
cd backend
pytest

# Run with coverage
pytest --cov=app tests/
```

## 🚧 Roadmap

- [x] Backend API dengan FastAPI
- [x] Frontend Dashboard dengan Streamlit
- [x] Sensor Simulation
- [x] Alert System
- [x] Analytics Dashboard
- [ ] MQTT Integration
- [ ] Real Sensor Hardware Support
- [ ] Mobile App
- [ ] AI Prediction Models
- [ ] Multi-language Support

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

MIT License - lihat [LICENSE](LICENSE) untuk detail.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Streamlit](https://streamlit.io/) - Data apps framework
- [AI Kuera](https://github.com/kuera-ai) - AI Integration
- [eFishery](https://efishery.com/) - Inspiration for aquaculture tech

## 📞 Support

Untuk pertanyaan atau support:
- Email: support@mirofish.ai
- Issues: [GitHub Issues](https://github.com/yourusername/mirofish/issues)
- Documentation: [Wiki](https://github.com/yourusername/mirofish/wiki)

---

**Made with ❤️ for Indonesian Aquaculture**
