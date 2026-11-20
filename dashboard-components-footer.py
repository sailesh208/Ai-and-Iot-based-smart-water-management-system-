"""
AquaNest – Enterprise Footer Component
Renders a clean, multi-column enterprise footer matching Navy-Purplish Dark Mode
and Light Mode using native Streamlit columns and crisp cards, completely immune
to markdown code-block parsing artifacts.
"""

import streamlit as st


def render_footer(is_dark: bool = None):
    """Renders the comprehensive AquaNest enterprise footer matching the active theme."""
    if is_dark is None:
        is_dark = st.session_state.get("dark_theme", True)

    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#334155"
    text_muted = "#A5B4FC" if is_dark else "#64748B"
    border_color = "rgba(139, 92, 246, 0.35)" if is_dark else "rgba(226, 232, 240, 0.9)"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.88) 0%, rgba(22, 15, 56, 0.94) 100%)" if is_dark else "#FFFFFF"
    accent_blue = "#00F0FF" if is_dark else "#00A8E8"

    st.markdown(f"<div style='margin-top: 56px; border-top: 1px solid {border_color}; padding-top: 32px;'></div>", unsafe_allow_html=True)

    # 1. Live System Telemetry Strip
    st.markdown(f"""
<div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 14px; padding: 12px 20px; margin-bottom: 28px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="width: 8px; height: 8px; border-radius: 50%; background: #10B981; box-shadow: 0 0 10px #10B981;"></span>
        <span style="font-size: 0.82rem; font-weight: 800; color: #10B981; letter-spacing: 0.5px;">SYSTEM OPERATIONAL</span>
        <span style="font-size: 0.82rem; color: {text_sub};">• Java 21 Spring Boot 3 Core (Port 8080)</span>
    </div>
    <div style="display: flex; flex-wrap: wrap; gap: 16px; font-size: 0.8rem; color: {text_sub};">
        <span>🔥 <b>Firestore:</b> aquanest-d4f40</span>
        <span>📡 <b>MQTT:</b> localhost:1883</span>
        <span>🧠 <b>AI:</b> IsolationForest Active</span>
        <span>⚡ <b>Uptime:</b> 99.98%</span>
    </div>
</div>
""", unsafe_allow_html=True)

    # 2. 4-Column Enterprise Information Grid
    fc1, fc2, fc3, fc4 = st.columns([1.4, 1.1, 1.1, 1.3], gap="medium")

    with fc1:
        st.markdown(f"""
<div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 20px; height: 100%;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #00A8E8, #6366F1); display: flex; align-items: center; justify-content: center; font-size: 18px; color: white;">💧</div>
        <div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 800; color: {text_main}; line-height: 1;">AquaNest</div>
            <div style="font-size: 0.62rem; font-weight: 800; color: {accent_blue}; letter-spacing: 1px; text-transform: uppercase;">Smart Water Infrastructure</div>
        </div>
    </div>
    <p style="color: {text_sub}; font-size: 0.84rem; line-height: 1.6; margin-bottom: 14px;">
        Autonomous IoT water telemetry, dual-threshold hysteresis pump protection, Scikit-Learn nocturnal leak analytics, and fair pulse-meter billing for residential apartment communities.
    </p>
    <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); padding: 4px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; color: #10B981;">
        <span style="width: 6px; height: 6px; border-radius: 50%; background: #10B981;"></span>
        Zero Water Waste Initiative
    </div>
</div>
""", unsafe_allow_html=True)

    with fc2:
        st.markdown(f"""
<div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 20px; height: 100%;">
    <div style="font-family: 'Outfit', sans-serif; font-size: 0.98rem; font-weight: 800; color: {text_main}; margin-bottom: 12px; letter-spacing: 0.5px;">
        PLATFORM MODULES
    </div>
    <div style="font-size: 0.84rem; color: {text_sub}; line-height: 2.0;">
        <div><span style="color: {accent_blue};">◈</span> Overhead Tank Sensing</div>
        <div><span style="color: #10B981;">⚙️</span> Pump Hysteresis (20%–90%)</div>
        <div><span style="color: #F59E0B;">🛡️</span> AI Leakage Detector</div>
        <div><span style="color: #6366F1;">▥</span> Pulse Sub-Metering (Flats 101–120)</div>
        <div><span style="color: #EC4899;">↗</span> 7-Day ML Demand Forecast</div>
        <div><span style="color: #10B981;">₹</span> Smart Formula Invoicing</div>
    </div>
</div>
""", unsafe_allow_html=True)

    with fc3:
        st.markdown(f"""
<div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 20px; height: 100%;">
    <div style="font-family: 'Outfit', sans-serif; font-size: 0.98rem; font-weight: 800; color: {text_main}; margin-bottom: 12px; letter-spacing: 0.5px;">
        SYSTEM ARCHITECTURE
    </div>
    <div style="font-size: 0.84rem; color: {text_sub}; line-height: 2.0;">
        <div><span style="color: {accent_blue};">☁️</span> Firebase Cloud Firestore</div>
        <div><span style="color: #6366F1;">⚡</span> Java 21 / Spring Boot 3 Engine</div>
        <div><span style="color: #10B981;">📡</span> Eclipse Paho MQTT v3.1.1 Broker</div>
        <div><span style="color: #F59E0B;">🧠</span> Scikit-Learn Anomaly Model</div>
        <div><span style="color: {accent_blue};">📟</span> ESP32 Edge Node + JSN-SR04T</div>
        <div><span style="color: #10B981;">🔒</span> Role-Based RBAC Flat Isolation</div>
    </div>
</div>
""", unsafe_allow_html=True)

    with fc4:
        st.markdown(f"""
<div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 20px; height: 100%;">
    <div style="font-family: 'Outfit', sans-serif; font-size: 0.98rem; font-weight: 800; color: {text_main}; margin-bottom: 12px; letter-spacing: 0.5px;">
        DISPATCH & HELP DESK
    </div>
    <div style="font-size: 0.84rem; color: {text_sub}; line-height: 1.8; margin-bottom: 12px;">
        <div><b>🚨 Emergency Hotline:</b> <span style="color: #EF4444; font-weight: 700;">+91 (800) AQUA-NEST</span></div>
        <div><b>🏢 Facility Office:</b> Tower A, Maintenance Bay 2</div>
        <div><b>✉️ Admin Dispatch:</b> admin@aquanest.io</div>
        <div><b>💬 Resident Desk:</b> support@aquanest.io</div>
    </div>
    <div style="background: rgba(0,0,0,0.2); border: 1px solid {border_color}; border-radius: 8px; padding: 6px 12px; font-size: 0.76rem; color: {text_muted};">
        ⏱️ <b>Response SLA:</b> Leakage response &lt; 15 mins
    </div>
</div>
""", unsafe_allow_html=True)

    # 3. Bottom Legal & Privacy Bar
    st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; padding-top: 22px; margin-top: 24px; border-top: 1px solid {border_color}; font-size: 0.8rem; color: {text_muted};">
    <div>
        © 2026 <b>AquaNest Smart Apartment Water Management System</b>. All rights reserved.
    </div>
    <div style="display: flex; gap: 18px; flex-wrap: wrap;">
        <span>⚡ 99.98% Telemetry Uptime</span>
        <span>🔒 ISO 27001 Data Privacy</span>
        <span>🌱 Eco-Resilient Community Standard</span>
        <span>v2.4.0-Production</span>
    </div>
</div>
""", unsafe_allow_html=True)
