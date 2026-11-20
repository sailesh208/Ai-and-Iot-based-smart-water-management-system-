"""
AquaNest – Smart Apartment Water Management System
Master Streamlit Application Entry Point
Integrates Java Spring Boot REST API, AI/ML models, and AquaNest Design System.
"""

import streamlit as st
import streamlit.components.v1 as components

# Streamlit Page Config
st.set_page_config(
    page_title="AquaNest – Smart Apartment Water Management System",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State early
if "dark_theme" not in st.session_state:
    st.session_state["dark_theme"] = True

if "user" not in st.session_state or st.session_state["user"] is None:
    # Default to Admin user for instant access to admin views
    st.session_state["user"] = {
        "userId": "USR_ADMIN",
        "name": "System Admin",
        "email": "admin@aquanest.io",
        "role": "ADMIN",
        "houseId": "MAIN"
    }

if "nav_selection" not in st.session_state or st.session_state["nav_selection"] == "AI Assistant":
    st.session_state["nav_selection"] = "Home"

if "auto_refresh" not in st.session_state:
    st.session_state["auto_refresh"] = False

from utils.theme import inject_custom_css
from services.api_client import AquaNestApiClient

# Inject custom AquaNest theme styling (respects dark_theme session state)
inject_custom_css()

# Instantiate API client & check connectivity
if "api_client" not in st.session_state:
    st.session_state["api_client"] = AquaNestApiClient()

api_client = st.session_state["api_client"]

# Import Views
from views.home_view import render_home_page
from views.auth_view import render_login_view, render_signup_view, render_forgot_password_view
from views.admin_dashboard_view import render_admin_dashboard
from views.tank_monitoring_view import render_tank_monitoring
from views.pump_control_view import render_pump_control
from views.leakage_detection_view import render_leakage_detection
from views.water_consumption_view import render_water_consumption
from views.ai_analytics_view import render_ai_analytics
from views.demand_forecast_view import render_demand_forecast
from views.smart_billing_view import render_smart_billing
from views.apartments_view import render_apartments_view
from views.alerts_view import render_alerts_view
from views.reports_view import render_reports_view
from views.settings_view import render_settings_view
from views.resident_portal_view import render_resident_portal
from views.ai_assistant_view import render_ai_assistant_view, render_ai_assistant_dialog
from views.data_collection_view import render_data_collection_view

current_page = st.session_state.get("nav_selection", "Home")
current_user = st.session_state.get("user") or {"role": "ADMIN", "name": "System Admin"}

# -------------------------------------------------------------
# SIDEBAR VISIBILITY LOGIC
# (Sidebar is HIDDEN on Home / Public Pages, ACTIVE on Dashboard & Operations Views)
# -------------------------------------------------------------
if current_page in ["Home", "Login", "Sign Up", "Forgot Password"]:
    # Completely hide sidebar on landing and auth pages
    st.markdown("""
    <style>
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapseButton"] {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    # Render rich Admin / Resident Navigation Sidebar
    with st.sidebar:
        # Brand Identity
        st.markdown("""
        <div style="padding: 10px 4px 16px 4px; border-bottom: 1px solid rgba(139, 92, 246, 0.25); margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #00F0FF 0%, #6366F1 100%);
                            display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 14px rgba(0, 240, 255, 0.4);">
                    💧
                </div>
                <div>
                    <div style="font-size: 18px; font-weight: 900; color: #FFFFFF; letter-spacing: -0.5px;">AquaNest</div>
                    <div style="font-size: 10px; font-weight: 700; color: #00F0FF; letter-spacing: 1.2px;">SMART WATER SYSTEM</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Admin / Resident Profile Badge
        if current_user.get("role") == "ADMIN":
            st.markdown("""
            <div style="background: rgba(30, 19, 74, 0.85); border: 1px solid rgba(139, 92, 246, 0.35); border-radius: 12px;
                        padding: 10px 14px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="font-size: 20px;">👑</div>
                    <div>
                        <div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">System Admin</div>
                        <div style="font-size: 10px; color: #10B981; font-weight: 600;">● Full Infrastructure Control</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: rgba(30, 19, 74, 0.85); border: 1px solid rgba(139, 92, 246, 0.35); border-radius: 12px;
                        padding: 10px 14px; margin-bottom: 16px;">
                <div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">{current_user.get('name', 'Resident')}</div>
                <div style="font-size: 10px; color: #00F0FF; font-weight: 600;">Unit: {current_user.get('houseId', 'H101')}</div>
            </div>
            """, unsafe_allow_html=True)

        def navigate(label, route, icon, help_text):
            is_active = st.session_state["nav_selection"] == route
            if st.button(
                f"{icon}  {label}",
                key=f"sidebar_nav_{route.lower().replace(' ', '_')}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                help=help_text
            ):
                st.session_state["nav_selection"] = route
                st.rerun()

        # Main Navigation
        navigate("Dashboard", "Dashboard" if current_user.get("role") == "ADMIN" else "Resident Dashboard", "🎛️", "Admin Command Center & KPI Overview")

        if current_user.get("role") == "ADMIN":
            with st.expander("💧  Water Management", expanded=st.session_state["nav_selection"] in ["Tank Monitoring", "Pump Control", "Water Consumption"]):
                navigate("Tank Monitoring", "Tank Monitoring", "◈", "Overhead tank level & TDS telemetry")
                navigate("Pump Control", "Pump Control", "⚙", "2.0 HP Lift Pump manual/auto controls")
                navigate("Water Consumption", "Water Consumption", "▥", "Building-wide flow audit & trends")

            with st.expander("🚨  Safety & Leakage", expanded=st.session_state["nav_selection"] in ["Leakage Detection", "Alerts"]):
                navigate("Leakage Detection", "Leakage Detection", "⌁", "AI IsolationForest acoustic radar")
                navigate("System Alerts", "Alerts", "!", "Incident dispatch & escalation queue")

            with st.expander("✦  AI & Analytics", expanded=st.session_state["nav_selection"] in ["AI Analytics", "Demand Forecast"]):
                navigate("AI Anomaly Analytics", "AI Analytics", "✦", "Nocturnal anomaly scores & charts")
                navigate("Demand Forecast", "Demand Forecast", "↗", "7-Day predictive demand models")

            with st.expander("🏢  Apartments & Tariffs", expanded=st.session_state["nav_selection"] in ["Apartments", "Smart Billing"]):
                navigate("Apartments", "Apartments", "⌂", "20-apartment pulse sub-meter telemetry")
                navigate("Smart Billing", "Smart Billing", "₹", "Volumetric tiered water tariffs")

            with st.expander("⚙️  Administration", expanded=st.session_state["nav_selection"] in ["Reports", "Data Collection", "Settings"]):
                navigate("Reports", "Reports", "▤", "Export operational audit reports")
                navigate("Data Collection", "Data Collection", "🧾", "Manually enter, import, and expand telemetry datasets")
                navigate("System Settings", "Settings", "⚙", "Hardware thresholds & Firestore sync")
        else:
            navigate("My Consumption", "My Consumption", "▥", "Review your apartment water usage")
            navigate("My Bill", "My Bill", "₹", "Review your water bill")
            navigate("Alerts", "Alerts", "!", "View active system alerts")
            navigate("Recommendations", "Recommendations", "✦", "View personalized water advice")

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        navigate("Public Home", "Home", "🏠", "Return to public landing page")

        st.divider()

        # Quick Utility Controls in Sidebar
        sb_c1, sb_c2 = st.columns(2)
        with sb_c1:
            if st.button("🔄 Sync", key="sb_sync_btn", use_container_width=True, help="Synchronize backend telemetry"):
                st.toast("Telemetry synchronized.", icon="🔄")
                st.rerun()
        with sb_c2:
            if st.button("💧 Pulse", key="sb_pulse_btn", use_container_width=True, help="Step IoT sensor simulation"):
                ok, msg = api_client.step_iot_simulation()
                if ok:
                    st.toast(msg, icon="💧")
                    st.rerun()

        # Light / Dark theme toggle in sidebar
        is_dark_theme = st.session_state.get("dark_theme", True)
        if st.button("☀️ Light Mode" if is_dark_theme else "🌙 Dark Mode", key="sb_theme_toggle", use_container_width=True):
            st.session_state["dark_theme"] = not is_dark_theme
            st.rerun()

        if st.button("🚪 Log Out", key="authenticated_sidebar_logout", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["nav_selection"] = "Home"
            st.rerun()

# Main Content Area Router
current_page = st.session_state["nav_selection"]
user = st.session_state.get("user")
role = user.get("role") if user else "PUBLIC"
house_id = user.get("houseId") if user else None
user_name = user.get("name") if user else "Resident"
api_client.demo_mode = bool(user and user.get("demo"))

if current_page == "Home":
    render_home_page()
elif current_page == "Login":
    render_login_view(api_client)
elif current_page == "Sign Up":
    render_signup_view(api_client)
elif current_page == "Forgot Password":
    render_forgot_password_view()
elif current_page == "Dashboard":
    render_admin_dashboard(api_client)
elif current_page == "AI Assistant":
    render_ai_assistant_view(api_client, user_role=role, user_house_id=house_id, user_name=user_name)
elif current_page == "Tank Monitoring":
    render_tank_monitoring(api_client)
elif current_page == "Pump Control":
    render_pump_control(api_client, user_role=role)
elif current_page == "Leakage Detection":
    render_leakage_detection(api_client)
elif current_page in ["Water Consumption", "My Consumption"]:
    render_water_consumption(api_client, user_role=role, user_house_id=house_id)
elif current_page == "AI Analytics":
    render_ai_analytics(api_client, user_role=role, user_house_id=house_id)
elif current_page == "Demand Forecast":
    render_demand_forecast(api_client, user_role=role, user_house_id=house_id)
elif current_page in ["Smart Billing", "My Bill"]:
    render_smart_billing(api_client, user_role=role, user_house_id=house_id)
elif current_page == "Apartments":
    render_apartments_view(api_client, user_role=role)
elif current_page == "Alerts":
    render_alerts_view(api_client, user_role=role, user_house_id=house_id)
elif current_page == "Reports":
    render_reports_view(api_client, user_role=role)
elif current_page == "Data Collection":
    render_data_collection_view(user_role=role)
elif current_page == "Settings":
    render_settings_view(api_client, user_role=role)
elif current_page in ["Resident Dashboard", "Recommendations"]:
    render_resident_portal(api_client, user_house_id=house_id or "H101", user_name=user_name)
else:
    render_home_page()

# Enterprise Multi-Column Footer
from components.footer import render_footer
render_footer()

# Floating Chat Widget (Fixed in bottom-right corner)
st.markdown("""
<style>
div.st-key-floating_chat_icon,
div[class*="st-key-floating_chat_icon"] {
    position: fixed !important;
    bottom: 26px !important;
    right: 28px !important;
    z-index: 999999 !important;
}

div.st-key-floating_chat_icon > button,
div[class*="st-key-floating_chat_icon"] > button,
div[class*="st-key-floating_chat_icon"] button {
    background: linear-gradient(135deg, #00F0FF 0%, #6366F1 100%) !important;
    background-color: #6366F1 !important;
    color: #FFFFFF !important;
    border-radius: 50% !important;
    width: 62px !important;
    height: 62px !important;
    min-width: 62px !important;
    max-width: 62px !important;
    padding: 0 !important;
    font-size: 28px !important;
    box-shadow: 0 8px 30px rgba(0, 240, 255, 0.5) !important;
    border: 2px solid rgba(255, 255, 255, 0.7) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    animation: floatChatGlow 3s ease-in-out infinite alternate !important;
}

div.st-key-floating_chat_icon > button:hover,
div[class*="st-key-floating_chat_icon"] > button:hover {
    transform: scale(1.15) translateY(-4px) !important;
    box-shadow: 0 12px 35px rgba(0, 240, 255, 0.85) !important;
}

@keyframes floatChatGlow {
    0% { transform: translateY(0px); box-shadow: 0 8px 25px rgba(0, 240, 255, 0.4); }
    100% { transform: translateY(-6px); box-shadow: 0 14px 35px rgba(99, 102, 241, 0.75); }
}
</style>
""", unsafe_allow_html=True)

if st.button("💬", key="floating_chat_icon", help="Open AquaNest AI Assistant"):
    render_ai_assistant_dialog(api_client, user_role=role, user_house_id=house_id, user_name=user_name)
