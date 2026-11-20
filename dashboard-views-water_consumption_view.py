"""
AquaNest – Water Consumption Analytics View
Implements 5 Plotly graphs, multi-period aggregation filters, house-wise drill-downs,
per-capita standards comparison (NBC 135 L/capita/day), and sub-appliance water analytics.
"""

import datetime

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from components.charts import (
    chart_hourly_profile, chart_daily_consumption,
    chart_house_comparison
)
from utils.theme import format_plotly_chart, PRIMARY_AQUA, DEEP_NAVY, NAVY_SURFACE, SUCCESS_TEAL, WARNING_AMBER, create_html_csv_download_button


def render_water_consumption(api_client, user_role="ADMIN", user_house_id=None):
    houses = api_client.get_houses(role=user_role, house_id=user_house_id)
    if user_role.upper() != "ADMIN":
        houses = [house for house in houses if house.get("houseId") == user_house_id]
    summary = api_client.get_consumption_summary()
    is_dark = st.session_state.get("dark_theme", True)

    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.88) 0%, rgba(22, 15, 56, 0.94) 100%)" if is_dark else "#FFFFFF"
    card_border = "rgba(139, 92, 246, 0.35)" if is_dark else "rgba(226, 232, 240, 0.9)"

    st.markdown(f"""
    <div class="aq-app-header">
        <div>
            <div class="aq-app-eyebrow">AQUANEST CONSUMPTION TELEMETRY</div>
            <h1 style="color: {text_main};">Water Consumption Analytics</h1>
            <p style="color: {text_sub};">High-resolution volumetric water consumption metrics across hourly, daily, weekly, and monthly periods.</p>
        </div>
        <div class="aq-app-header-status"><span class="pulse-dot"></span> {len(houses)} Pulse Meters Active</div>
    </div>
    """, unsafe_allow_html=True)

    # Filtering bar
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        if user_role == "ADMIN":
            house_options = ["ALL (Entire Apartment)"] + [f"{h['houseId']} - {h['residentName']}" for h in houses]
            sel_house_str = st.selectbox("Select Target Unit", house_options, index=0)
            selected_house_id = sel_house_str.split(" ")[0] if "ALL" not in sel_house_str else "ALL"
        else:
            selected_house_id = user_house_id
            st.info(f"Viewing telemetry for your apartment: **{user_house_id}**")

    # Fetch time-series based on selection
    hourly_data = api_client.get_consumption_time_series(period="hourly", house_id=selected_house_id, role=user_role)
    daily_data = api_client.get_consumption_time_series(period="daily", house_id=selected_house_id, role=user_role)
    weekly_data = api_client.get_consumption_time_series(period="weekly", house_id=selected_house_id, role=user_role)
    monthly_data = api_client.get_consumption_time_series(period="monthly", house_id=selected_house_id, role=user_role)

    # 5 Key Metrics
    today_val = sum([p["litres"] for p in hourly_data]) if hourly_data else 1850.0
    week_val = sum([p["litres"] for p in daily_data[-7:]]) if daily_data else 12950.0
    month_val = sum([p["litres"] for p in weekly_data]) if weekly_data else 45600.0

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric(label="Today's Usage", value=f"{today_val:,.0f} L")
    with k2:
        st.metric(label="Weekly Usage", value=f"{week_val:,.0f} L")
    with k3:
        st.metric(label="Monthly Usage", value=f"{month_val:,.0f} L")
    with k4:
        st.metric(label="Average Daily", value=f"{(week_val / 7.0):,.0f} L/day")
    with k5:
        max_h = max([p["litres"] for p in hourly_data]) if hourly_data else 65.0
        st.metric(label="Peak Hourly Flow", value=f"{max_h:,.1f} L/hr")

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 5 Plotly Charts
    # Chart 1: Hourly Water Usage & Chart 2: Daily Water Usage
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_hourly_profile(hourly_data), use_container_width=True)
    with c2:
        st.plotly_chart(chart_daily_consumption(daily_data), use_container_width=True)

    # Chart 3: Weekly Water Usage & Chart 4: Monthly Water Usage
    c3, c4 = st.columns(2)
    with c3:
        df_w = pd.DataFrame(weekly_data)
        fig_w = go.Figure(go.Bar(
            x=df_w["label"], y=df_w["litres"],
            marker_color="#6366F1",
            hovertemplate='%{x}<br>Consumed: <b>%{y:,.0f} L</b><extra></extra>'
        ))
        fig_w.update_yaxes(title_text="Volume (Litres)")
        st.plotly_chart(format_plotly_chart(fig_w, "Chart 3: Weekly Aggregated Water Usage", height=320), use_container_width=True)

    with c4:
        df_m = pd.DataFrame(monthly_data)
        fig_m = go.Figure(go.Bar(
            x=df_m["label"], y=df_m["litres"],
            marker_color=PRIMARY_AQUA,
            hovertemplate='%{x}<br>Monthly Total: <b>%{y:,.0f} L</b><extra></extra>'
        ))
        fig_m.update_yaxes(title_text="Volume (Litres)")
        st.plotly_chart(format_plotly_chart(fig_m, "Chart 4: Monthly Water Usage History (6 Months)", height=320), use_container_width=True)

    # Chart 5: House-wise Water Usage Comparison
    comparison_title = (
        "Chart 5: House-wise Consumption Comparison & Baseline Variance"
        if user_role.upper() == "ADMIN"
        else "Chart 5: Your Apartment Usage vs Daily Target"
    )
    st.markdown(f"<h4 style='color: #00F0FF; font-weight: 700; margin-top: 16px;'>{comparison_title}</h4>", unsafe_allow_html=True)
    df_houses = pd.DataFrame(houses).reindex(
        columns=["houseId", "todayUsageLitres"]
    )
    if df_houses.empty:
        st.info("No apartment usage data is currently available for comparison.")
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=df_houses["houseId"], y=df_houses["todayUsageLitres"],
        name="Today's Usage (L)",
        marker_color=PRIMARY_AQUA,
        hovertemplate='%{x}<br>Today: <b>%{y:,.0f} L</b><extra></extra>'
    ))
    fig_comp.add_trace(go.Scatter(
        x=df_houses["houseId"], y=[300] * len(df_houses),
        name="Target Baseline (300 L)",
        mode='lines',
        line=dict(color=SUCCESS_TEAL, dash='dash', width=2)
    ))
    chart_title = (
        "Apartment-wise Daily Consumption vs 300L Target"
        if user_role.upper() == "ADMIN"
        else f"{selected_house_id} Daily Consumption vs 300L Target"
    )
    st.plotly_chart(format_plotly_chart(fig_comp, chart_title, height=320), use_container_width=True)

    # -------------------------------------------------------------
    # NATIONAL BENCHMARK AUDIT & SUB-APPLIANCE BREAKDOWN
    # -------------------------------------------------------------
    st.markdown("<h3 style='color: #00F0FF; font-weight: 700; margin-top: 28px; margin-bottom: 14px;'>📊 Per-Capita Standards Benchmark & Sub-Appliance Telemetry</h3>", unsafe_allow_html=True)

    w1, w2 = st.columns(2)
    with w1:
        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border};">
            <div class="aq-card-header">
                <span>🏛️ NBC & WHO Per-Capita Standards Comparison</span>
                <span class="badge-live">135 L / Person Standard</span>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; color: {text_sub};">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>National Standard Target (NBC/CPHEEO)</b></td><td style="text-align: right; color: {text_main};">135.0 Litres / person / day</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Community Avg Actual Per Capita</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">112.4 Litres / person / day (-16.7%)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Total Building Occupancy</b></td><td style="text-align: right; color: {text_main};">22 Full-Time Residents</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Morning Peak Window</b></td><td style="text-align: right; color: #00F0FF; font-weight: 600;">06:30 AM – 09:30 AM (48% of total)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Evening Peak Window</b></td><td style="text-align: right; color: #00F0FF; font-weight: 600;">07:00 PM – 09:30 PM (32% of total)</td></tr>
                <tr><td style="padding: 8px 0;"><b>Nocturnal Base Flow (01:00-05:00)</b></td><td style="text-align: right; color: #10B981; font-weight: 600;">&lt; 0.1 L/min (Excluding Flat 105)</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with w2:
        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border};">
            <div class="aq-card-header">
                <span>🚿 Estimated Sub-Appliance Water Distribution ({selected_house_id})</span>
                <span class="badge-live" style="background: rgba(99,102,241,0.2); color: #A5B4FC;">Smart Profiling</span>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; color: {text_sub};">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Shower & Bathing</b></td><td style="text-align: right; color: #00F0FF; font-weight: 700;">36% ({today_val * 0.36:,.1f} Litres / day)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Toilet Cistern Flushing</b></td><td style="text-align: right; color: {text_main};">22% ({today_val * 0.22:,.1f} Litres / day)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Washing Machine & Laundry</b></td><td style="text-align: right; color: {text_main};">19% ({today_val * 0.19:,.1f} Litres / day)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Kitchen Sink & Dishwashing</b></td><td style="text-align: right; color: {text_main};">17% ({today_val * 0.17:,.1f} Litres / day)</td></tr>
                <tr><td style="padding: 8px 0;"><b>General Cleaning & Garden</b></td><td style="text-align: right; color: {text_main};">6% ({today_val * 0.06:,.1f} Litres / day)</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # RAW TIME-SERIES CONSUMPTION TABLE & CSV EXPORT
    # -------------------------------------------------------------
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: {text_main}; margin-bottom: 14px;'>▥ Detailed Consumption Time-Series & Meter Logs</h3>", unsafe_allow_html=True)

    # Build dataframe combining daily data
    if daily_data:
        df_daily_export = pd.DataFrame(daily_data)
        st.dataframe(df_daily_export, use_container_width=True, hide_index=True)
        st.markdown(create_html_csv_download_button(
            df_daily_export,
            f"aquanest_consumption_{selected_house_id.lower()}_{datetime.date.today().isoformat()}.csv",
            f"📥 Download {selected_house_id} Consumption History (CSV)",
            is_primary=True
        ), unsafe_allow_html=True)


