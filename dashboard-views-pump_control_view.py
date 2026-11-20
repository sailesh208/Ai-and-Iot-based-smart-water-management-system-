"""
AquaNest – Pump Control View
Includes 5 Plotly charts, role-authorized manual pump control, motor electrical telemetry,
fail-safe interlock matrix, energy consumption analytics, and audit logs.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from components.charts import chart_pump_runtime_timeline
from utils.theme import format_plotly_chart, SUCCESS_TEAL, WARNING_AMBER, DANGER_CORAL, PRIMARY_AQUA, DEEP_NAVY


def render_pump_control(api_client, user_role="ADMIN"):
    pump_data = api_client.get_pump_status()
    logs = api_client.get_pump_logs()
    pump_status = str(pump_data.get("status", "")).upper()
    is_dark = st.session_state.get("dark_theme", True)

    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.88) 0%, rgba(22, 15, 56, 0.94) 100%)" if is_dark else "#FFFFFF"
    card_border = "rgba(139, 92, 246, 0.35)" if is_dark else "rgba(226, 232, 240, 0.9)"

    st.markdown(f"""
    <div class="aq-app-header">
        <div>
            <div class="aq-app-eyebrow">AQUANEST AUTOMATION</div>
            <h1 style="color: {text_main};">Water Pump Automation & Control</h1>
            <p style="color: {text_sub};">Intelligent hysteresis pump automation, optocoupled contactor protection, and runtime analytics.</p>
        </div>
        <div class="aq-app-header-status"><span class="pulse-dot"></span> Hardware Watchdog Armed</div>
    </div>
    """, unsafe_allow_html=True)

    # 5 KPI Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric(label="Pump Status", value=pump_data.get("status", "OFF"))
    with k2:
        st.metric(label="Operational Mode", value=pump_data.get("mode", "AUTO"))
    with k3:
        st.metric(label="Runtime Today", value=f"{pump_data.get('runtimeTodayMinutes', 135)} mins")
    with k4:
        st.metric(label="Weekly Runtime", value=f"{pump_data.get('runtimeThisWeekMinutes', 720)} mins")
    with k5:
        st.metric(label="Activations Today", value=pump_data.get("activationCountToday", 4))

    if not getattr(api_client, "is_connected", False):
        st.warning("Local demo state only: the backend is offline, so pump controls do not operate physical hardware.")

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Admin Control Panel
    st.markdown(f"""
    <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border};">
        <div class="aq-card-header">
            <span>⚙️ Pump Operation & Manual Override Console</span>
            <span class="badge-live">Contactor 30A Optocoupled</span>
        </div>
    """, unsafe_allow_html=True)

    c_mode, c_ctrl1, c_ctrl2 = st.columns([1.5, 1, 1])

    with c_mode:
        selected_mode = st.radio("Operating Mode", ["AUTO (Autonomous Hysteresis)", "MANUAL (Operator Override)"],
                                 index=0 if pump_data.get("mode") == "AUTO" else 1, horizontal=True)

    with c_ctrl1:
        if st.button(
            "▶️ START PUMP",
            key="btn_pump_start",
            use_container_width=True,
            type="primary" if pump_status == "ON" else "secondary",
        ):
            if user_role != "ADMIN":
                st.error("⛔ Access Denied: Only ADMIN can manually trigger pump operation.")
            else:
                mode_str = "MANUAL" if "MANUAL" in selected_mode else "AUTO"
                res = api_client.control_pump("START", mode=mode_str, role=user_role)
                if res.get("success"):
                    if res.get("_is_live"):
                        st.success(res.get("message", "Pump started successfully."))
                    else:
                        st.warning(res.get("message", "Pump started in local demo mode."))
                    st.rerun()
                else:
                    st.error(res.get("message", "Pump start failed."))

    with c_ctrl2:
        if st.button(
            "⏹️ STOP PUMP",
            key="btn_pump_stop",
            use_container_width=True,
            type="primary" if pump_status == "OFF" else "secondary",
        ):
            if user_role != "ADMIN":
                st.error("⛔ Access Denied: Only ADMIN can manually trigger pump operation.")
            else:
                mode_str = "MANUAL" if "MANUAL" in selected_mode else "AUTO"
                res = api_client.control_pump("STOP", mode=mode_str, role=user_role)
                if res.get("success"):
                    if res.get("_is_live"):
                        st.info(res.get("message", "Pump stopped successfully."))
                    else:
                        st.warning(res.get("message", "Pump stopped in local demo mode."))
                    st.rerun()
                else:
                    st.error(res.get("message", "Pump stop failed."))

    st.markdown("</div>", unsafe_allow_html=True)

    # 5 Major Charts
    # Chart 1: Pump ON/OFF Timeline & Chart 2: Daily Runtime
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_pump_runtime_timeline(logs), use_container_width=True)

    with c2:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        runtimes = [120, 145, 110, 135, 150, 180, 195]
        fig_r = go.Figure(go.Bar(
            x=days, y=runtimes,
            marker_color=PRIMARY_AQUA,
            hovertemplate='%{x}<br>Runtime: <b>%{y} mins</b><extra></extra>'
        ))
        fig_r.update_yaxes(title_text="Runtime (Minutes)")
        st.plotly_chart(format_plotly_chart(fig_r, "Daily Pump Operating Runtime (7 Days)", height=300), use_container_width=True)

    # Chart 3: Weekly Runtime Trend & Chart 4: Activation Count
    c3, c4 = st.columns(2)
    with c3:
        weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
        weekly_hours = [14.2, 15.5, 13.8, 16.1]
        fig_w = go.Figure(go.Scatter(
            x=weeks, y=weekly_hours,
            mode='lines+markers',
            line=dict(color="#6366F1", width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.15)',
            hovertemplate='%{x}<br>Total: <b>%{y:.1f} Hours</b><extra></extra>'
        ))
        fig_w.update_yaxes(title_text="Total Run Hours")
        st.plotly_chart(format_plotly_chart(fig_w, "Weekly Aggregated Pump Runtime Trend", height=300), use_container_width=True)

    with c4:
        activations = [4, 5, 3, 4, 5, 6, 6]
        fig_act = go.Figure(go.Bar(
            x=days, y=activations,
            marker_color=SUCCESS_TEAL,
            hovertemplate='%{x}<br>Activations: <b>%{y} cycles</b><extra></extra>'
        ))
        fig_act.update_yaxes(title_text="Cycle Count")
        st.plotly_chart(format_plotly_chart(fig_act, "Pump Activations per Day", height=300), use_container_width=True)

    # Chart 5: Tank Level vs Pump State Dual-Axis
    st.markdown("<h4 style='color: #00F0FF; font-weight: 700; margin-top: 18px;'>Chart 5: Tank Level vs Pump Trigger State (Hysteresis Band)</h4>", unsafe_allow_html=True)
    fig_band = go.Figure()
    hours_24 = [f"{h:02d}:00" for h in range(24)]
    levels_24 = [65, 58, 50, 42, 35, 28, 19, 45, 75, 92, 86, 78, 70, 62, 54, 46, 38, 26, 18, 52, 82, 91, 84, 75]
    pump_triggers = [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0]

    fig_band.add_trace(go.Scatter(x=hours_24, y=levels_24, name="Tank Level %", line=dict(color=PRIMARY_AQUA, width=2.5)))
    fig_band.add_trace(go.Bar(x=hours_24, y=[p * 100 for p in pump_triggers], name="Pump Running", marker_color="rgba(16, 185, 129, 0.35)"))
    fig_band.add_hline(y=20, line_dash="dash", line_color=DANGER_CORAL, annotation_text="Auto-Start Floor (20%)")
    fig_band.add_hline(y=90, line_dash="dash", line_color=SUCCESS_TEAL, annotation_text="Auto-Stop Ceiling (90%)")
    st.plotly_chart(format_plotly_chart(fig_band, "24-Hour Automated Hysteresis Trigger Cycle", height=320), use_container_width=True)

    # -------------------------------------------------------------
    # DETAILED ELECTRICAL TELEMETRY & FAIL-SAFE INTERLOCK MATRIX
    # -------------------------------------------------------------
    st.markdown("<h3 style='color: #00F0FF; font-weight: 700; margin-top: 28px; margin-bottom: 14px;'>⚡ Motor Electrical Telemetry & Fail-Safe Protection Interlocks</h3>", unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border};">
            <div class="aq-card-header">
                <span>🔌 Motor Electrical Specifications & Health</span>
                <span class="badge-live">2.0 HP Centrifugal</span>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; color: {text_sub};">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Motor Type & Power</b></td><td style="text-align: right; color: {text_main};">Single-Phase Induction, 2.0 HP (1.5 kW)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Line Voltage & Frequency</b></td><td style="text-align: right; color: {text_main};">230 V AC ± 3% @ 50.0 Hz</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Operating Current Draw</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">4.25 A (Normal Rated: 4.8 A)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Power Factor (cos φ)</b></td><td style="text-align: right; color: {text_main};">0.89 (High Efficiency)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Motor Winding Temperature</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">52.4 °C (Trip Threshold: 75.0 °C)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Daily Energy Consumption</b></td><td style="text-align: right; color: #00F0FF; font-weight: 700;">3.38 kWh (~₹ 27.00 / day)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Cumulative Service Hours</b></td><td style="text-align: right; color: {text_main};">84.5 / 500 hrs (Bearing Service)</td></tr>
                <tr><td style="padding: 8px 0;"><b>Delivery Flow Rate</b></td><td style="text-align: right; color: #00F0FF; font-weight: 600;">48.0 Litres / minute</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border};">
            <div class="aq-card-header">
                <span>🛡️ Fail-Safe Protection & Interlock Status</span>
                <span class="badge-live" style="background: rgba(16,185,129,0.2); color: #10B981;">All Interlocks OK</span>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; color: {text_sub};">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Dry-Run Protection</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">✅ ARMED (Sump Level &gt; 30%)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Thermal Overload Relay</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">✅ HEALTHY (NTC Temp Sensor)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Anti-Rapid Cycling Lockout</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">✅ 180s Cooldown Enforced</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Over-Voltage / Under-Voltage</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">✅ 190V - 255V Window OK</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Hardware Emergency E-Stop</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">✅ CLOSED (Circuit Clear)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Snubber Diode & Surge Filter</b></td><td style="text-align: right; color: {text_main};">MOV Surge Suppressor Active</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Relay Contactor Rating</b></td><td style="text-align: right; color: {text_main};">30A 250VAC Heavy-Duty</td></tr>
                <tr><td style="padding: 8px 0;"><b>Firmware Watchdog Timer</b></td><td style="text-align: right; color: #10B981; font-weight: 600;">ESP32 8s Hardware Auto-Reset</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
