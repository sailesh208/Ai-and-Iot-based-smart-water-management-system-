"""
AquaNest – System Settings View (Admin Only)
Configuration for tank dimensions, pump hysteresis thresholds, water tariffs,
IoT calibration, MQTT broker endpoints, and Google Cloud Firebase Firestore Database connectivity.
"""

import streamlit as st
import os
from services.firebase_service import get_firebase_service


def render_settings_view(api_client, user_role="ADMIN"):
    if user_role != "ADMIN":
        st.error("⛔ Access Denied: System configuration is restricted to Administrators.")
        return

    settings = api_client.get_settings()
    fb_service = get_firebase_service()
    fb_stats = fb_service.test_connection()
    is_dark = st.session_state.get("dark_theme", True)

    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.88) 0%, rgba(22, 15, 56, 0.94) 100%)" if is_dark else "#FFFFFF"
    card_border = "rgba(139, 92, 246, 0.35)" if is_dark else "rgba(226, 232, 240, 0.9)"

    st.markdown(f"""
    <div class="aq-app-header">
        <div>
            <div class="aq-app-eyebrow">AQUANEST SYSTEM CONTROL</div>
            <h1 style="color: {text_main};">System Configuration & Parameters</h1>
            <p style="color: {text_sub};">Configure physical tank geometry, pump hysteresis bands, billing tariffs, and Firebase Cloud Database.</p>
        </div>
        <div class="aq-app-header-status"><span class="pulse-dot"></span> Admin Control Active</div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 1. Firebase Cloud Firestore Integration Section
    # -------------------------------------------------------------
    with st.expander("🔥 Firebase Cloud Firestore Database Connection", expanded=True):
        st.markdown(f"<h4 style='color: #00F0FF; font-weight: 700; margin-bottom: 12px;'>Firebase Database Status & Synchronization</h4>", unsafe_allow_html=True)

        col_st1, col_st2, col_st3 = st.columns(3)
        with col_st1:
            if fb_stats["is_connected"]:
                st.markdown("""
                <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #10B981;">CONNECTION STATUS</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #10B981; margin-top: 4px;">🟢 Live Cloud Firestore</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #F59E0B;">CONNECTION STATUS</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #F59E0B; margin-top: 4px;">🟡 Local Firestore Cache</div>
                </div>
                """, unsafe_allow_html=True)

        with col_st2:
            st.markdown(f"""
            <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="font-size: 0.8rem; font-weight: 700; color: {text_sub};">FIRESTORE PROJECT</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #00F0FF; margin-top: 4px;"><code>{fb_stats['project_id']}</code></div>
            </div>
            """, unsafe_allow_html=True)

        with col_st3:
            total_synced_docs = sum(fb_stats["collections"].values())
            st.markdown(f"""
            <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="font-size: 0.8rem; font-weight: 700; color: {text_sub};">TOTAL DOCUMENTS</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #10B981; margin-top: 4px;">{total_synced_docs} Records</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

        # Firestore Collections Breakdown
        st.markdown(f"<div style='font-size: 0.9rem; font-weight: 700; color: {text_main}; margin-bottom: 8px;'>📦 Cloud Firestore Collections:</div>", unsafe_allow_html=True)
        cols = st.columns(4)
        col_names = list(fb_stats["collections"].keys())
        for idx, cname in enumerate(col_names):
            c_target = cols[idx % 4]
            count = fb_stats["collections"][cname]
            with c_target:
                st.markdown(f"""
                <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 8px; margin-bottom: 8px; text-align: center;">
                    <div style="font-size: 0.8rem; color: #A5B4FC;"><code>{cname}</code></div>
                    <div style="font-size: 1rem; font-weight: 700; color: {text_main};">{count} docs</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

        # Interactive Firebase Action Buttons
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("🚀 Seed & Sync All to Firestore", key="btn_seed_firestore", use_container_width=True):
                with st.spinner("Seeding standard collections and demo telemetry to Firestore..."):
                    res = fb_service.seed_initial_collections()
                    st.success(f"✅ Successfully seeded {sum(res.values())} documents across 8 collections to Firestore!")
                    st.rerun()

        with btn_col2:
            if st.button("🔄 Test Connection & Refresh", key="btn_test_firestore", use_container_width=True):
                st.rerun()

        with btn_col3:
            key_path_input = st.text_input("Service Account Key Path", value="firebase-service-account.json", help="Path to your Google Firebase private key JSON file")

        if st.button("🔑 Connect Service Account Key", key="btn_connect_key"):
            if os.path.exists(key_path_input):
                success, msg = fb_service.connect_with_credentials_file(key_path_input)
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning(f"File not found at '{key_path_input}'. Place your Firebase service account JSON in the project root or specify full path.")

    # -------------------------------------------------------------
    # 2. Main System Settings Form
    # -------------------------------------------------------------
    with st.form("settings_form"):
        st.markdown(f"<h4 style='color: #00F0FF; font-weight: 700;'>1. Overhead Tank & Pump Thresholds</h4>", unsafe_allow_html=True)
        s_c1, s_c2, s_c3 = st.columns(3)
        with s_c1:
            tank_cap = st.number_input("Tank Capacity (Litres)", min_value=500.0, max_value=20000.0, value=float(settings.get("tankCapacityLitres", 4000.0)), step=250.0)
        with s_c2:
            low_th = st.slider("Low Level Pump-ON Threshold (%)", min_value=10.0, max_value=40.0, value=float(settings.get("lowThresholdPercent", 20.0)), step=1.0)
        with s_c3:
            full_th = st.slider("Full Level Pump-OFF Threshold (%)", min_value=75.0, max_value=98.0, value=float(settings.get("fullThresholdPercent", 90.0)), step=1.0)

        st.markdown(f"<h4 style='color: #00F0FF; font-weight: 700; margin-top: 20px;'>2. Smart Billing & Water Tariffs</h4>", unsafe_allow_html=True)
        b_c1, b_c2, b_c3 = st.columns(3)
        with b_c1:
            tariff = st.number_input("Water Rate (₹ per Litre)", min_value=0.01, max_value=5.0, value=float(settings.get("waterTariffPerLitre", 0.10)), step=0.01, format="%.2f")
        with b_c2:
            fixed_ch = st.number_input("Fixed Monthly Maintenance Charge (₹)", min_value=0.0, max_value=5000.0, value=float(settings.get("fixedMonthlyCharge", 200.0)), step=50.0)
        with b_c3:
            due_days = st.number_input("Invoice Payment Due Window (Days)", min_value=5, max_value=30, value=int(settings.get("billingDueDays", 10)))

        st.markdown(f"<h4 style='color: #00F0FF; font-weight: 700; margin-top: 20px;'>3. IoT Calibration & Diagnostics Thresholds</h4>", unsafe_allow_html=True)
        i_c1, i_c2, i_c3 = st.columns(3)
        with i_c1:
            calib = st.number_input("Flow Meter Calibration (Pulses / Litre)", min_value=100.0, max_value=1000.0, value=float(settings.get("flowCalibrationFactor", 450.0)), step=10.0)
        with i_c2:
            press_th = st.number_input("Pipe Leak Pressure Alarm Threshold (bar)", min_value=0.5, max_value=2.5, value=float(settings.get("pressureThresholdBar", 1.8)), step=0.1)
        with i_c3:
            leak_tol = st.number_input("Distribution Mismatch Tolerance (%)", min_value=1.0, max_value=15.0, value=float(settings.get("leakageTolerancePercent", 5.0)), step=0.5)

        st.markdown(f"<h4 style='color: #00F0FF; font-weight: 700; margin-top: 20px;'>4. System Execution Mode</h4>", unsafe_allow_html=True)
        demo_toggle = st.checkbox("Enable Simulation & Autonomous Demo Mode (Simulate Telemetry)", value=settings.get("demoMode", True))

        save_btn = st.form_submit_button("💾 Save System Configuration", use_container_width=True)

        if save_btn:
            new_settings = {
                "tankCapacityLitres": tank_cap,
                "lowThresholdPercent": low_th,
                "fullThresholdPercent": full_th,
                "waterTariffPerLitre": tariff,
                "fixedMonthlyCharge": fixed_ch,
                "billingDueDays": due_days,
                "flowCalibrationFactor": calib,
                "pressureThresholdBar": press_th,
                "leakageTolerancePercent": leak_tol,
                "demoMode": demo_toggle,
                "billingCycle": "MONTHLY",
                "abnormalUsageThreshold": 1.7,
                "notificationEmail": "admin@aquanest.io"
            }
            api_client.update_settings(new_settings, role="ADMIN")
            fb_service.save_document("settings", "global_config", new_settings)
            st.success("✅ System settings saved successfully. Thresholds updated across Java backend, Firestore, and hysteresis loop.")
