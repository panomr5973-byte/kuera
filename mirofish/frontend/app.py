"""
Mirofish AI - Streamlit Frontend
Dashboard Smart Aquaculture
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8080")
REFRESH_INTERVAL = 10  # seconds

# Page config
st.set_page_config(
    page_title="Mirofish AI - Smart Aquaculture",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0066cc;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .alert-critical {
        background-color: #ffcccc;
        border-left: 5px solid #ff0000;
        padding: 10px;
        margin: 5px 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
    }
    .status-healthy {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-critical {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def fetch_data(endpoint: str):
    """Fetch data from API."""
    try:
        response = requests.get(f"{API_URL}/api/v1/{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


def post_data(endpoint: str, data: dict):
    """Post data to API."""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/{endpoint}",
            json=data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error posting data: {e}")
        return None


def render_sidebar():
    """Render sidebar navigation."""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/fish.png", width=80)
        st.title("Mirofish AI")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "🏢 Farms", "🌊 Ponds", "📊 Analytics", "⚙️ Simulation", "ℹ️ About"]
        )
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("Quick Actions")
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        # API Status
        health = fetch_data("health")
        if health:
            st.success("🟢 API Connected")
        else:
            st.error("🔴 API Disconnected")
        
        return page


def render_dashboard():
    """Render main dashboard."""
    st.markdown('<p class="main-header">🐟 Mirofish AI Dashboard</p>', unsafe_allow_html=True)
    
    # Fetch summary data
    summary = fetch_data("dashboard/summary")
    
    if not summary:
        st.warning("No data available. Please check API connection.")
        return
    
    # Overview metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Farms", summary["overview"]["total_farms"])
    with col2:
        st.metric("Ponds", summary["overview"]["total_ponds"])
    with col3:
        st.metric("Active Ponds", summary["overview"]["active_ponds"])
    with col4:
        st.metric("Sensors", summary["overview"]["total_sensors"])
    with col5:
        st.metric("Readings (24h)", summary["overview"]["readings_24h"])
    
    st.markdown("---")
    
    # Alerts section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚨 Active Alerts")
        
        alerts = summary.get("alerts", {})
        
        if alerts.get("critical", 0) > 0:
            st.error(f"🔴 {alerts['critical']} Critical Alerts")
        
        if alerts.get("warning", 0) > 0:
            st.warning(f"🟡 {alerts['warning']} Warning Alerts")
        
        if alerts.get("total_active", 0) == 0:
            st.success("✅ No active alerts - All systems normal")
    
    with col2:
        st.subheader("System Health")
        health_status = summary.get("system_health", {})
        
        if health_status.get("status") == "healthy":
            st.markdown('<p class="status-healthy">🟢 HEALTHY</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-critical">🔴 DEGRADED</p>', unsafe_allow_html=True)
        
        st.write(f"Ponds Online: {health_status.get('ponds_online', 'N/A')}")
    
    st.markdown("---")
    
    # Farms overview
    st.subheader("🏢 Farms Overview")
    
    farms = fetch_data("farms")
    if farms:
        for farm in farms[:5]:  # Show first 5 farms
            with st.expander(f"📍 {farm['name']} ({farm.get('pond_count', 0)} ponds)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Location:** {farm.get('location', 'N/A')}")
                    st.write(f"**Coordinates:** {farm.get('latitude', 'N/A')}, {farm.get('longitude', 'N/A')}")
                
                with col2:
                    if farm.get('description'):
                        st.write(f"**Description:** {farm['description']}")
                    
                    if st.button("View Details", key=f"farm_{farm['id']}"):
                        st.session_state.selected_farm = farm['id']
                        st.session_state.page = "🏢 Farms"
                        st.rerun()


def render_farms():
    """Render farms management page."""
    st.header("🏢 Farm Management")
    
    farms = fetch_data("farms")
    
    if not farms:
        st.info("No farms found. Create your first farm!")
        
        # Create farm form
        with st.form("create_farm"):
            st.subheader("Create New Farm")
            name = st.text_input("Farm Name *")
            location = st.text_input("Location")
            lat = st.number_input("Latitude", value=0.0, format="%.6f")
            lng = st.number_input("Longitude", value=0.0, format="%.6f")
            description = st.text_area("Description")
            
            if st.form_submit_button("Create Farm"):
                if name:
                    result = post_data("farms", {
                        "name": name,
                        "location": location,
                        "latitude": lat if lat != 0 else None,
                        "longitude": lng if lng != 0 else None,
                        "description": description
                    })
                    
                    if result:
                        st.success(f"Farm '{name}' created successfully!")
                        st.rerun()
                else:
                    st.error("Farm name is required")
        
        return
    
    # Display farms
    for farm in farms:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.subheader(f"📍 {farm['name']}")
                st.write(f"Location: {farm.get('location', 'N/A')}")
                st.write(f"Ponds: {farm.get('pond_count', 0)}")
            
            with col2:
                if farm.get('latitude') and farm.get('longitude'):
                    st.write(f"Lat: {farm['latitude']:.6f}")
                    st.write(f"Lng: {farm['longitude']:.6f}")
            
            with col3:
                if st.button("View", key=f"view_{farm['id']}"):
                    st.session_state.selected_farm = farm['id']
                    st.rerun()
            
            st.markdown("---")


def render_ponds():
    """Render ponds management page."""
    st.header("🌊 Pond Management")
    
    # Get farms for dropdown
    farms = fetch_data("farms")
    
    if not farms:
        st.warning("Please create a farm first.")
        return
    
    # Farm selection
    farm_options = {f['name']: f['id'] for f in farms}
    selected_farm_name = st.selectbox("Select Farm", list(farm_options.keys()))
    selected_farm_id = farm_options[selected_farm_name]
    
    # Get ponds for selected farm
    ponds = fetch_data(f"ponds?farm_id={selected_farm_id}")
    
    if not ponds:
        st.info("No ponds found. Create your first pond!")
    
    # Create pond form
    with st.expander("➕ Create New Pond"):
        with st.form("create_pond"):
            name = st.text_input("Pond Name *")
            volume = st.number_input("Volume (Liters)", min_value=0, value=0)
            fish_type = st.selectbox("Fish Type", ["Tilapia", "Catfish", "Carp", "Koi", "Other"])
            fish_count = st.number_input("Fish Count", min_value=0, value=0)
            
            if st.form_submit_button("Create Pond"):
                if name:
                    result = post_data("ponds", {
                        "farm_id": selected_farm_id,
                        "name": name,
                        "volume_liters": volume if volume > 0 else None,
                        "fish_type": fish_type,
                        "fish_count": fish_count
                    })
                    
                    if result:
                        st.success(f"Pond '{name}' created!")
                        
                        # Initialize sensors
                        sensor_result = fetch_data(f"ponds/{result['id']}/sensors/initialize")
                        if sensor_result:
                            st.info(f"Initialized {len(sensor_result.get('sensors', []))} sensors")
                        
                        st.rerun()
    
    # Display ponds
    if ponds:
        for pond in ponds:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    status_color = "🟢" if pond['status'] == 'active' else "🔴"
                    st.subheader(f"{status_color} {pond['name']}")
                    st.write(f"Fish: {pond.get('fish_type', 'N/A')} ({pond.get('fish_count', 0)})")
                    if pond.get('volume_liters'):
                        st.write(f"Volume: {pond['volume_liters']:,} L")
                
                with col2:
                    # Get latest readings
                    latest = fetch_data(f"readings/pond/{pond['id']}/latest")
                    if latest and latest.get('readings'):
                        readings = latest['readings']
                        
                        if 'ph' in readings:
                            st.write(f"pH: {readings['ph']['value']}")
                        if 'dissolved_o2' in readings:
                            st.write(f"DO: {readings['dissolved_o2']['value']} mg/L")
                        if 'temperature' in readings:
                            st.write(f"Temp: {readings['temperature']['value']}°C")
                
                with col3:
                    if st.button("Monitor", key=f"monitor_{pond['id']}"):
                        st.session_state.selected_pond = pond['id']
                        st.session_state.page = "📊 Analytics"
                        st.rerun()
                
                st.markdown("---")


def render_analytics():
    """Render analytics page."""
    st.header("📊 Analytics & Monitoring")
    
    # Get all ponds
    ponds = fetch_data("ponds")
    
    if not ponds:
        st.warning("No ponds available. Create a pond first.")
        return
    
    # Pond selection
    pond_options = {f"{p['name']} ({p.get('fish_type', 'Unknown')})": p['id'] for p in ponds}
    selected_pond_name = st.selectbox("Select Pond", list(pond_options.keys()))
    selected_pond_id = pond_options[selected_pond_name]
    
    # Get pond dashboard data
    dashboard_data = fetch_data(f"dashboard/pond/{selected_pond_id}/status")
    
    if not dashboard_data:
        st.error("Failed to load pond data")
        return
    
    pond_info = dashboard_data.get('pond', {})
    readings = dashboard_data.get('latest_readings', {})
    alerts = dashboard_data.get('active_alerts', [])
    
    # Pond info
    st.subheader(f"🌊 {pond_info.get('name', 'Unknown')}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Fish Type", pond_info.get('fish_type', 'N/A'))
    with col2:
        st.metric("Fish Count", pond_info.get('fish_count', 0))
    with col3:
        st.metric("Active Alerts", len(alerts))
    with col4:
        status = pond_info.get('status', 'unknown')
        st.metric("Status", status.upper())
    
    st.markdown("---")
    
    # Current readings
    st.subheader("📊 Current Readings")
    
    if readings:
        col1, col2, col3, col4 = st.columns(4)
        
        reading_cols = [
            ('ph', 'pH Level', 'pH', 'bluered'),
            ('dissolved_o2', 'Dissolved O2', 'mg/L', 'blues'),
            ('temperature', 'Temperature', '°C', 'oranges'),
            ('conductivity', 'Conductivity', 'μS/cm', 'greens')
        ]
        
        for col, (key, label, unit, color) in zip([col1, col2, col3, col4], reading_cols):
            with col:
                if key in readings:
                    value = readings[key].get('value', 0)
                    status = readings[key].get('status', 'unknown')
                    
                    # Determine delta color
                    delta_color = "normal"
                    if status == "critical":
                        delta_color = "inverse"
                    elif status == "warning":
                        delta_color = "off"
                    
                    st.metric(
                        label=label,
                        value=f"{value:.2f} {unit}" if value else "N/A",
                        delta=status.upper() if status != "normal" else None,
                        delta_color=delta_color
                    )
    else:
        st.info("No readings available. Start simulation to generate data.")
    
    st.markdown("---")
    
    # Alerts
    if alerts:
        st.subheader("🚨 Active Alerts")
        
        for alert in alerts:
            severity = alert.get('severity', 'info')
            if severity == 'critical':
                st.error(f"🔴 **{alert.get('parameter', 'Unknown')}**: {alert.get('message', '')}")
            elif severity == 'warning':
                st.warning(f"🟡 **{alert.get('parameter', 'Unknown')}**: {alert.get('message', '')}")
            else:
                st.info(f"🔵 **{alert.get('parameter', 'Unknown')}**: {alert.get('message', '')}")
    
    # Recommendations
    recommendations = dashboard_data.get('recommendations', [])
    if recommendations:
        st.subheader("💡 Recommendations")
        
        for rec in recommendations:
            priority = rec.get('priority', 'medium')
            icon = "🔴" if priority == "high" or priority == "critical" else "🟡" if priority == "medium" else "🔵"
            st.write(f"{icon} **{rec.get('action', '')}**")
            st.caption(f"Parameter: {rec.get('parameter', 'Unknown')} | Current: {rec.get('current_value', 'N/A')}")


def render_simulation():
    """Render simulation control page."""
    st.header("⚙️ Sensor Simulation")
    
    st.markdown("""
    Simulasi sensor memungkinkan Anda menguji sistem tanpa hardware fisik.
    Data sensor akan dibuat secara otomatis dengan variasi realistis.
    """)
    
    # Get all ponds
    ponds = fetch_data("ponds")
    
    if not ponds:
        st.warning("No ponds available. Create a pond first.")
        return
    
    # Simulation status
    sim_status = fetch_data("simulation/all")
    
    if sim_status:
        st.subheader("📊 Active Simulations")
        
        simulators = sim_status.get('simulators', [])
        if simulators:
            for sim in simulators:
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{sim.get('name', 'Unknown')}**")
                    st.caption(f"ID: {sim.get('pond_id', 'N/A')[:8]}...")
                
                with col2:
                    running = "🟢 Running" if sim.get('running') else "🔴 Stopped"
                    mode = sim.get('mode', 'normal')
                    st.write(f"{running} | Mode: {mode}")
                
                with col3:
                    if sim.get('running'):
                        if st.button("Stop", key=f"stop_{sim['pond_id']}"):
                            fetch_data(f"simulation/stop/{sim['pond_id']}")
                            st.rerun()
        else:
            st.info("No active simulations")
    
    st.markdown("---")
    
    # Start simulation
    st.subheader("🚀 Start New Simulation")
    
    pond_options = {p['name']: p['id'] for p in ponds}
    selected_pond = st.selectbox("Select Pond", list(pond_options.keys()))
    selected_pond_id = pond_options[selected_pond]
    
    col1, col2 = st.columns(2)
    
    with col1:
        mode = st.selectbox(
            "Simulation Mode",
            ["normal", "critical", "fluctuating", "drifting"],
            help="""
            - Normal: Data dalam range normal
            - Critical: Data di luar threshold (untuk testing alert)
            - Fluctuating: Data dengan variasi tinggi
            - Drifting: Data dengan tren perubahan
            """
        )
    
    with col2:
        interval = st.slider("Interval (seconds)", 5, 60, 10)
    
    if st.button("▶️ Start Simulation", type="primary"):
        result = post_data(f"simulation/start/{selected_pond_id}", {
            "mode": mode,
            "interval_seconds": interval
        })
        
        if result:
            st.success(f"Simulation started for {selected_pond} in {mode} mode")
            st.rerun()
    
    # Generate single reading
    st.markdown("---")
    st.subheader("🎲 Generate Test Reading")
    
    if st.button("Generate Single Reading"):
        result = fetch_data(f"simulation/generate/{selected_pond_id}")
        
        if result:
            st.json(result)


def render_about():
    """Render about page."""
    st.header("ℹ️ About Mirofish AI")
    
    st.markdown("""
    ## 🐟 Mirofish AI - Smart Aquaculture System
    
    **Mirofish AI** adalah sistem monitoring budidaya perikanan pintar berbasis IoT dan AI.
    Sistem ini dirancang untuk membantu petani ikan memantau kualitas air dan kondisi kolam secara real-time.
    
    ### ✨ Features
    
    - **📊 Real-time Monitoring**: Pantau pH, DO, suhu, dan parameter lainnya secara real-time
    - **🚨 Smart Alerts**: Notifikasi otomatis ketika parameter di luar batas aman
    - **📈 Analytics**: Analisis tren dan prediksi kondisi kolam
    - **🎮 Simulation**: Uji sistem tanpa hardware fisik
    - **🤖 AI Integration**: Terintegrasi dengan AI Kuera untuk rekomendasi pintar
    
    ### 🏗️ Architecture
    
    - **Backend**: FastAPI (Python)
    - **Frontend**: Streamlit
    - **Database**: SQLite
    - **Simulation**: Python Asyncio
    
    ### 📋 Supported Sensors
    
    | Sensor | Parameter | Unit |
    |--------|-----------|------|
    | pH | pH Level | pH |
    | DO | Dissolved Oxygen | mg/L |
    | Temperature | Water Temperature | °C |
    | Conductivity | Electrical Conductivity | μS/cm |
    | Turbidity | Water Clarity | NTU |
    | Ammonia | NH3 Level | mg/L |
    
    ### 📞 Support
    
    Untuk informasi lebih lanjut, hubungi tim pengembang atau kunjungi dokumentasi.
    
    ---
    
    **Version**: 1.0.0  
    **License**: MIT  
    **Author**: AI Development Team
    """)
    
    # System status
    st.subheader("🔧 System Status")
    
    status = fetch_data("status")
    if status:
        st.json(status)


def main():
    """Main application entry point."""
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "🏠 Dashboard"
    
    # Render sidebar and get selected page
    selected_page = render_sidebar()
    
    # Override with session state if set
    page = st.session_state.get('page', selected_page)
    
    # Render selected page
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "🏢 Farms":
        render_farms()
    elif page == "🌊 Ponds":
        render_ponds()
    elif page == "📊 Analytics":
        render_analytics()
    elif page == "⚙️ Simulation":
        render_simulation()
    elif page == "ℹ️ About":
        render_about()


if __name__ == "__main__":
    main()
