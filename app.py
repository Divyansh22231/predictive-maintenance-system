import streamlit as st
import requests
import os

# Configuration must be the first Streamlit command
st.set_page_config(
    page_title="Predictive Maintenance",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ---------------------------------------------------------
# Custom CSS for React Dashboard Replication
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Reduce top empty space */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Card containers */
    .dashboard-card {
        background-color: #151e32;
        border: 1px solid #1e293b;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    .status-badge-low {
        border: 1px solid #10b981;
        color: #10b981;
        padding: 0.4rem 1rem;
        border-radius: 0.25rem;
        font-weight: 600;
        text-align: center;
        background-color: rgba(16, 185, 129, 0.1);
        display: inline-block;
    }
    .status-badge-medium {
        border: 1px solid #f59e0b;
        color: #f59e0b;
        padding: 0.4rem 1rem;
        border-radius: 0.25rem;
        font-weight: 600;
        text-align: center;
        background-color: rgba(245, 158, 11, 0.1);
        display: inline-block;
    }
    .status-badge-high {
        border: 1px solid #ef4444;
        color: #ef4444;
        padding: 0.4rem 1rem;
        border-radius: 0.25rem;
        font-weight: 600;
        text-align: center;
        background-color: rgba(239, 68, 68, 0.1);
        display: inline-block;
    }
    
    .backend-status {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
        border-radius: 1rem;
        font-weight: bold;
        float: right;
    }
    .backend-online {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid #10b981;
    }
    .backend-offline {
        background-color: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid #ef4444;
    }
    
    /* Value texts */
    .metric-value {
        font-size: 1.25rem;
        font-weight: 600;
        color: #f8fafc;
        margin-top: 0.2rem;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0;
    }
    
    /* Section headers */
    .card-header {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input Subtexts */
    .input-subtext {
        font-size: 0.7rem; 
        color: #64748b; 
        margin-top: -12px; 
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# State & Presets
# ---------------------------------------------------------
if 'air_temp' not in st.session_state:
    st.session_state.air_temp = 298.1
if 'process_temp' not in st.session_state:
    st.session_state.process_temp = 308.6
if 'rot_speed' not in st.session_state:
    st.session_state.rot_speed = 1551.0
if 'torque' not in st.session_state:
    st.session_state.torque = 42.8
if 'tool_wear' not in st.session_state:
    st.session_state.tool_wear = 0.0
if 'machine_type' not in st.session_state:
    st.session_state.machine_type = "M"
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

def set_preset(preset_name):
    if preset_name == "Normal Operation":
        st.session_state.air_temp = 298.1
        st.session_state.process_temp = 308.6
        st.session_state.rot_speed = 1551.0
        st.session_state.torque = 42.8
        st.session_state.tool_wear = 0.0
        st.session_state.machine_type = "M"
    elif preset_name == "Tool Wear Critical":
        st.session_state.air_temp = 298.1
        st.session_state.process_temp = 308.6
        st.session_state.rot_speed = 1551.0
        st.session_state.torque = 42.8
        st.session_state.tool_wear = 240.0
        st.session_state.machine_type = "M"
    elif preset_name == "High Torque Overload":
        st.session_state.air_temp = 300.0
        st.session_state.process_temp = 310.0
        st.session_state.rot_speed = 1400.0
        st.session_state.torque = 70.0
        st.session_state.tool_wear = 50.0
        st.session_state.machine_type = "L"
    elif preset_name == "High Speed Low Torque":
        st.session_state.air_temp = 295.0
        st.session_state.process_temp = 305.0
        st.session_state.rot_speed = 2500.0
        st.session_state.torque = 15.0
        st.session_state.tool_wear = 10.0
        st.session_state.machine_type = "H"

def on_submit():
    st.session_state.submitted = True

# ---------------------------------------------------------
# Layout
# ---------------------------------------------------------
@st.cache_data(ttl=10)
def check_health():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return r.status_code == 200
    except:
        return False

is_online = check_health()

# Top Header
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("<h2 style='margin-bottom: 0;'>⚙️ Predictive Maintenance</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Machine Failure Risk Monitoring & AI-Assisted Analysis</p>", unsafe_allow_html=True)
with header_col2:
    if is_online:
        st.markdown("<div class='backend-status backend-online'>🟢 Backend Online</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='backend-status backend-offline'>🔴 Backend Offline</div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color: #1e293b; margin-top: 0.5rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

# Main layout columns
left_col, right_col = st.columns([1.2, 2.5], gap="large")

with left_col:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>📊 Machine Operating Conditions</div>", unsafe_allow_html=True)
    
    st.markdown("<p class='metric-label' style='margin-bottom: 10px;'>QUICK TEST PRESETS</p>", unsafe_allow_html=True)
    
    p_col1, p_col2 = st.columns(2)
    p_col1.button("Normal Operation", use_container_width=True, on_click=set_preset, args=("Normal Operation",))
    p_col2.button("Tool Wear Critical", use_container_width=True, on_click=set_preset, args=("Tool Wear Critical",))
    p_col1.button("High Torque Overload", use_container_width=True, on_click=set_preset, args=("High Torque Overload",))
    p_col2.button("High Speed Low Torque", use_container_width=True, on_click=set_preset, args=("High Speed Low Torque",))
    
    st.markdown("<hr style='border-color: #1e293b; margin: 1rem 0;'>", unsafe_allow_html=True)
    
    with st.form("machine_inputs"):
        st.number_input("Air Temperature [K]", min_value=250.0, max_value=350.0, step=0.1, key="air_temp")
        st.markdown("<p class='input-subtext'>Operating ambient range: 250K - 350K</p>", unsafe_allow_html=True)
        
        st.number_input("Process Temperature [K]", min_value=250.0, max_value=350.0, step=0.1, key="process_temp")
        st.markdown("<p class='input-subtext'>Operating process range: 250K - 350K</p>", unsafe_allow_html=True)
        
        st.number_input("Rotational Speed [rpm]", min_value=500.0, max_value=5000.0, step=1.0, key="rot_speed")
        st.markdown("<p class='input-subtext'>Motor shaft rotation speed: 500 - 5000 rpm</p>", unsafe_allow_html=True)
        
        st.number_input("Torque [Nm]", min_value=0.0, max_value=200.0, step=0.1, key="torque")
        st.markdown("<p class='input-subtext'>Applied motor torque: 0 - 200 Nm</p>", unsafe_allow_html=True)
        
        st.number_input("Tool Wear [min]", min_value=0.0, max_value=500.0, step=1.0, key="tool_wear")
        st.markdown("<p class='input-subtext'>Accumulated tool wear time</p>", unsafe_allow_html=True)
        
        # Ensure state corresponds to list index
        machine_types = ["L", "M", "H"]
        mt_val = st.session_state.machine_type if st.session_state.machine_type in machine_types else "M"
        
        st.selectbox("Machine Type", options=machine_types, index=machine_types.index(mt_val), key="machine_type")
        
        st.form_submit_button("Analyze Machine Condition", type="primary", use_container_width=True, on_click=on_submit)
    
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    if not st.session_state.submitted:
        st.info("👈 Enter machine parameters on the left and click 'Analyze Machine Condition' to view the assessment.")
    else:
        payload = {
            "air_temperature": st.session_state.air_temp,
            "process_temperature": st.session_state.process_temp,
            "rotational_speed": st.session_state.rot_speed,
            "torque": st.session_state.torque,
            "tool_wear": st.session_state.tool_wear,
            "machine_type": st.session_state.machine_type
        }
        
        with st.spinner("Analyzing machine telemetry and generating AI explanation..."):
            try:
                response = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=30)
                if response.status_code == 200:
                    res = response.json()
                    
                    # 1. Main Assessment Card
                    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
                    st.markdown("<p class='metric-label' style='margin-bottom: 0.5rem;'>MACHINE STATUS ASSESSMENT</p>", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([3, 1])
                    prediction_color = "#ef4444" if res["failure_predicted"] else "#10b981"
                    prediction_text = "Machine Failure Predicted" if res["failure_predicted"] else "No Machine Failure"
                    
                    c1.markdown(f"<h2 style='color: {prediction_color}; margin-top: 0;'>{prediction_text}</h2>", unsafe_allow_html=True)
                    
                    risk = res["risk_level"]
                    risk_class = f"status-badge-{risk.lower()}"
                    c2.markdown(f"""
                    <div style='text-align: right;'>
                        <p class='metric-label' style='margin-bottom: 4px;'>RISK LEVEL</p>
                        <div class='{risk_class}'>{risk}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    prob = res["failure_probability"]
                    st.progress(prob)
                    st.markdown(f"<p style='color: #94a3b8; font-family: monospace; font-size: 0.9rem;'>Failure Probability: {(prob * 100):.1f}%</p>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # 2. Split Cards (Sensor Overview & Calculated Features)
                    card_col1, card_col2 = st.columns(2)
                    
                    with card_col1:
                        st.markdown("<div class='dashboard-card' style='height: 95%;'>", unsafe_allow_html=True)
                        st.markdown("<div class='card-header'>🔍 Sensor Overview</div>", unsafe_allow_html=True)
                        
                        so = res["sensor_overview"]
                        r1c1, r1c2 = st.columns(2)
                        r1c1.markdown(f"<p class='metric-label'>AIR TEMP</p><p class='metric-value'>{so['air_temperature']} <span style='font-size:0.8rem; color:#64748b;'>K</span></p>", unsafe_allow_html=True)
                        r1c2.markdown(f"<p class='metric-label'>PROCESS TEMP</p><p class='metric-value'>{so['process_temperature']} <span style='font-size:0.8rem; color:#64748b;'>K</span></p>", unsafe_allow_html=True)
                        
                        st.markdown("<hr style='border-color: #1e293b; margin: 0.8rem 0;'>", unsafe_allow_html=True)
                        
                        r2c1, r2c2 = st.columns(2)
                        r2c1.markdown(f"<p class='metric-label'>ROTATIONAL SPEED</p><p class='metric-value'>{so['rotational_speed']} <span style='font-size:0.8rem; color:#64748b;'>rpm</span></p>", unsafe_allow_html=True)
                        r2c2.markdown(f"<p class='metric-label'>TORQUE</p><p class='metric-value'>{so['torque']} <span style='font-size:0.8rem; color:#64748b;'>Nm</span></p>", unsafe_allow_html=True)
                        
                        st.markdown("<hr style='border-color: #1e293b; margin: 0.8rem 0;'>", unsafe_allow_html=True)
                        
                        r3c1, r3c2 = st.columns(2)
                        r3c1.markdown(f"<p class='metric-label'>TOOL WEAR</p><p class='metric-value'>{so['tool_wear']} <span style='font-size:0.8rem; color:#64748b;'>min</span></p>", unsafe_allow_html=True)
                        r3c2.markdown(f"<p class='metric-label'>MACHINE TYPE</p><p class='metric-value'>Type-{so['machine_type']}</p>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    with card_col2:
                        st.markdown("<div class='dashboard-card' style='height: 95%;'>", unsafe_allow_html=True)
                        st.markdown("<div class='card-header'>📐 Calculated Features (Python)</div>", unsafe_allow_html=True)
                        
                        cf = res["calculated_features"]
                        f1, f2 = st.columns(2)
                        f1.markdown(f"<p class='metric-label'>TEMP DIFFERENCE</p><p class='metric-value' style='color:#0ea5e9;'>{cf['temperature_difference']:.2f} <span style='font-size:0.8rem; color:#64748b;'>K</span></p>", unsafe_allow_html=True)
                        f2.markdown(f"<p class='metric-label'>POWER</p><p class='metric-value' style='color:#0ea5e9;'>{cf['power']:.1f} <span style='font-size:0.8rem; color:#64748b;'>W</span></p>", unsafe_allow_html=True)
                        
                        st.markdown("<hr style='border-color: #1e293b; margin: 0.8rem 0;'>", unsafe_allow_html=True)
                        
                        st.markdown(f"<p class='metric-label'>WEAR-TORQUE PROD</p><p class='metric-value' style='color:#0ea5e9;'>{cf['wear_torque_product']:.1f} <span style='font-size:0.8rem; color:#64748b;'>min·Nm</span></p>", unsafe_allow_html=True)
                        
                        st.markdown("<hr style='border-color: #1e293b; margin: 0.8rem 0;'>", unsafe_allow_html=True)
                        
                        st.markdown("<p class='metric-label' style='margin-bottom: 0.5rem;'>IDENTIFIED OPERATING FACTORS:</p>", unsafe_allow_html=True)
                        
                        factors = res["potential_contributing_factors"]
                        if not factors:
                            st.markdown("<div style='border-left: 3px solid #f59e0b; padding-left: 10px; font-size: 0.9rem; color: #cbd5e1;'>Potential contributing factor: None identified (all operating conditions within normal parameters)</div>", unsafe_allow_html=True)
                        else:
                            for f in factors:
                                st.markdown(f"<div style='border-left: 3px solid #ef4444; padding-left: 10px; font-size: 0.9rem; color: #cbd5e1; margin-bottom: 5px;'>{f}</div>", unsafe_allow_html=True)
                                
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    # 3. AI Analysis Card
                    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
                    ai_c1, ai_c2 = st.columns([3, 1])
                    ai_c1.markdown("<div class='card-header'>🤖 AI Analysis</div>", unsafe_allow_html=True)
                    ai_c2.markdown("<div style='text-align: right;'><span style='background-color: #451a03; color: #f59e0b; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; border: 1px solid #78350f;'>Deterministic Fallback</span></div>" if res.get('ai_analysis', {}).get('is_fallback', False) else "", unsafe_allow_html=True)
                    
                    ai = res.get("ai_analysis", {})
                    
                    st.markdown("<p class='metric-label'>SUMMARY</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #e2e8f0; font-size: 0.95rem;'>{ai.get('summary', 'Analysis unavailable.')}</p>", unsafe_allow_html=True)
                    
                    st.markdown("<p class='metric-label' style='margin-top: 1rem;'>WHY THIS PREDICTION?</p>", unsafe_allow_html=True)
                    why_pred = ai.get('why_this_prediction')
                    if not why_pred:
                        why_pred = ai.get('why_prediction', 'N/A')
                    st.markdown(f"<p style='color: #e2e8f0; font-size: 0.95rem;'>{why_pred}</p>", unsafe_allow_html=True)
                    
                    st.markdown("<hr style='border-color: #1e293b; margin: 1rem 0;'>", unsafe_allow_html=True)
                    
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.markdown("<p class='metric-label'>MAINTENANCE RECOMMENDATION</p>", unsafe_allow_html=True)
                        st.info(ai.get('maintenance_recommendation', 'N/A'))
                    with m_col2:
                        st.markdown("<p class='metric-label'>OPERATIONAL ADVICE</p>", unsafe_allow_html=True)
                        st.success(ai.get('operational_advice', 'N/A'))
                        
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                else:
                    st.error(f"Backend Error: {response.status_code}\n{response.text}")
            except Exception as e:
                st.error(f"Could not connect to backend at {BACKEND_URL}. Error: {str(e)}")
