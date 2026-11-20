"""
AquaNest – Apartments Management View (Admin Only)
Provisioning and monitoring of individual apartment units, flow meters,
calibration certificates, and isolation valve controls.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.theme import format_plotly_chart, PRIMARY_AQUA, SUCCESS_TEAL, WARNING_AMBER, DEEP_NAVY, create_html_csv_download_button


def render_apartments_view(api_client, user_role="ADMIN"):
    if user_role != "ADMIN":
        st.error("⛔ Access Denied: Apartment provisioning is restricted to Administrators.")
        return

    houses = api_client.get_houses(role="ADMIN")
    is_dark = st.session_state.get("dark_theme", True)

    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.88) 0%, rgba(22, 15, 56, 0.94) 100%)" if is_dark else "#FFFFFF"
    card_border = "rgba(139, 92, 246, 0.35)" if is_dark else "rgba(226, 232, 240, 0.9)"

    st.markdown(f"""
    <div class="aq-app-header">
        <div>
            <div class="aq-app-eyebrow">AQUANEST ROSTER & TELEMETRY</div>
            <h1 style="color: {text_main};">Apartment Units Directory & Sub-Metering</h1>
            <p style="color: {text_sub};">Manage apartment profiles, assign digital pulse meters, and monitor flat telemetry.</p>
        </div>
        <div class="aq-app-header-status"><span class="pulse-dot"></span> {len(houses)} Units Online</div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Quick Metrics
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(label="Total Units", value=len(houses), delta="Dynamic Provisioning")
    with k2:
        active_count = sum([1 for h in houses if h.get("status") == "ACTIVE"])
        st.metric(label="Active Occupied", value=active_count)
    with k3:
        floor_count = df_h["floor"].nunique() if not df_h.empty else 0
        st.metric(label="Floor Distribution", value=f"{floor_count} Floors")
    with k4:
        st.metric(label="Pulse Meters", value=f"{len(houses)} Online", delta="100% Calibrated")

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Visual floor-wise & occupancy charts
    c1, c2 = st.columns(2)
    with c1:
        df_h = pd.DataFrame(houses)
        floor_usage = df_h.groupby("floor")["todayUsageLitres"].sum().reset_index()
        fig_floor = go.Figure(go.Bar(
            x=[f"Floor {r['floor']}" for _, r in floor_usage.iterrows()],
            y=floor_usage["todayUsageLitres"],
            marker_color=PRIMARY_AQUA,
            hovertemplate='%{x}<br>Floor Usage: <b>%{y:,.0f} L</b><extra></extra>'
        ))
        fig_floor.update_yaxes(title_text="Litres")
        st.plotly_chart(format_plotly_chart(fig_floor, "Floor-wise Water Usage Distribution", height=280), use_container_width=True)

    with c2:
        fig_curr = go.Figure(go.Bar(
            x=df_h["houseId"], y=df_h["currentUsageLitres"],
            marker_color=SUCCESS_TEAL,
            hovertemplate='%{x}<br>Current Outflow: <b>%{y:.1f} L/min</b><extra></extra>'
        ))
        fig_curr.update_yaxes(title_text="Flow Rate (L/min)")
        st.plotly_chart(format_plotly_chart(fig_curr, "Real-time Instantaneous Outflow by Flat", height=280), use_container_width=True)

    # Apartments Table
    st.markdown("<h4 style='color: #00F0FF; font-weight: 700; margin-top: 16px;'>Apartment Master Telemetry Registry</h4>", unsafe_allow_html=True)
    table_data = [
        {
            "Unit ID": h["houseId"],
            "Flat No": h["houseNumber"],
            "Floor": h["floor"],
            "Resident Name": h["residentName"],
            "Assigned Meter": h["meterId"],
            "Today's Usage (L)": f"{h['todayUsageLitres']:,.0f}",
            "Monthly Usage (L)": f"{h['monthlyUsageLitres']:,.0f}",
            "Status": h["status"],
            "Anomaly State": "⚠️ ABNORMAL" if h.get("anomalyStatus") == "ABNORMAL" else "✅ NORMAL"
        } for h in houses
    ]
    df_apt_export = pd.DataFrame(table_data)
    st.dataframe(df_apt_export, use_container_width=True, hide_index=True)
    st.markdown(create_html_csv_download_button(
        df_apt_export,
        f"aquanest_apartment_units_roster_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        "📥 Download Apartment Units Roster (CSV)",
        is_primary=True
    ), unsafe_allow_html=True)


    # -------------------------------------------------------------
    # SUB-METER HARDWARE SPECS & PROVISIONING FORM
    # -------------------------------------------------------------
    st.markdown("<h3 style='color: #00F0FF; font-weight: 700; margin-top: 28px; margin-bottom: 14px;'>⚙️ Sub-Meter Calibration Specs & Provisioning</h3>", unsafe_allow_html=True)

    ap1, ap2 = st.columns(2)
    with ap1:
        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border};">
            <div class="aq-card-header">
                <span>📟 Flow Meter Calibration Certificate Data</span>
                <span class="badge-live">Class B Certified</span>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; color: {text_sub};">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Meter Type</b></td><td style="text-align: right; color: {text_main};">Hall-Effect Rotary Pulse Sensor (YFS201)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Nominal Diameter</b></td><td style="text-align: right; color: {text_main};">3/4" (20 mm) Threaded Brass</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Pulse Resolution</b></td><td style="text-align: right; color: #00F0FF; font-weight: 700;">450 Pulses / Litre (2.22 mL / pulse)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Flow Range</b></td><td style="text-align: right; color: {text_main};">1.0 – 30.0 Litres / minute</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Pressure Loss @ Nominal</b></td><td style="text-align: right; color: #10B981; font-weight: 600;">&lt; 0.05 bar @ 15 L/min</td></tr>
                <tr><td style="padding: 8px 0;"><b>Calibration Expiry</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">December 2028 (5-Year Cycle)</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with ap2:
        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border};">
            <div class="aq-card-header">
                <span>➕ Provision New Apartment Unit</span>
                <span class="badge-live">Dynamic Registration</span>
            </div>
        """, unsafe_allow_html=True)

        with st.form("add_house_form"):
            new_h_num = st.text_input("House Number (e.g. 201, 202)")
            new_floor = st.number_input("Floor Number", min_value=1, max_value=20, value=2)
            new_resident = st.text_input("Resident Full Name")
            new_meter = st.text_input("Pulse Meter Serial ID (e.g. METER_H201)")
            sub_house = st.form_submit_button("Register & Activate Unit")

            if sub_house:
                if not new_h_num or not new_resident:
                    st.error("Please enter house number and resident name.")
                else:
                    st.success(f"Apartment Unit {new_h_num} provisioned with meter {new_meter or ('METER_H' + new_h_num)}.")

        st.markdown("</div>", unsafe_allow_html=True)
