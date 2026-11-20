"""
AquaNest – Resident Portal View
Strictly segregated personal apartment water monitoring, 5 Plotly charts, invoice breakdown,
interactive leak self-inspection checklist wizard, eco-rank scorecard, and AI recommendations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from components.charts import (
    chart_daily_consumption, chart_hourly_profile
)
from utils.theme import format_plotly_chart, PRIMARY_AQUA, SUCCESS_TEAL, WARNING_AMBER, DANGER_CORAL, NAVY_SURFACE, DEEP_NAVY, create_html_csv_download_button
from services.resident_profiles import RESIDENT_PROFILES


def render_resident_portal(api_client, user_house_id="H101", user_name="Resident"):
    # Enforce strictly isolated calls for this house only
    details = api_client.get_house_details(user_house_id, role="RESIDENT")
    hourly_cons = api_client.get_consumption_time_series(period="hourly", house_id=user_house_id, role="RESIDENT")
    daily_cons = api_client.get_consumption_time_series(period="daily", house_id=user_house_id, role="RESIDENT")
    weekly_cons = api_client.get_consumption_time_series(period="weekly", house_id=user_house_id, role="RESIDENT")
    monthly_cons = api_client.get_consumption_time_series(period="monthly", house_id=user_house_id, role="RESIDENT")
    bills = api_client.get_bills(role="RESIDENT", house_id=user_house_id)
    alerts = api_client.get_alerts(role="RESIDENT", house_id=user_house_id)
    recs = api_client.get_recommendations(role="RESIDENT", house_id=user_house_id)
    is_dark = st.session_state.get("dark_theme", True)

    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.88) 0%, rgba(22, 15, 56, 0.94) 100%)" if is_dark else "#FFFFFF"
    card_border = "rgba(139, 92, 246, 0.35)" if is_dark else "rgba(226, 232, 240, 0.9)"

    # Filter bills strictly to this house
    resident_bills = [b for b in bills if b.get("houseId") == user_house_id]
    latest_bill = resident_bills[0] if resident_bills else {
        "billingPeriod": "2026-09",
        "consumptionLitres": details.get("monthlyUsageLitres", 7200),
        "waterRate": 0.10,
        "waterCharge": 720.0,
        "fixedCharge": 200.0,
        "totalAmount": 920.0,
        "paymentStatus": "PENDING",
        "dueDate": "2026-10-10"
    }
    today_usage = float(details.get("todayUsageLitres", 280))
    community_average = float(details.get("apartmentAverageToday", today_usage))
    usage_difference = today_usage - community_average
    monthly_difference = abs(usage_difference) * 30
    difference_direction = "above" if usage_difference > 0 else "below"
    telemetry_status = details.get("anomalyStatus", "NORMAL")

    # Welcome Header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(20, 14, 52, 0.95) 0%, #0077B6 100%); padding: 30px 34px; border-radius: 18px; border: 1px solid {card_border}; color: white; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
        <div style="font-size: 0.82rem; color: #00F0FF; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">RESIDENT ECO-PORTAL</div>
        <h2 style="color: white; font-weight: 800; margin: 4px 0 8px 0;">Welcome, {user_name}</h2>
        <p style="color: #E2E8F0; font-size: 0.92rem; margin: 0;">
            Apartment Unit: <b>{details.get('houseNumber', '101')}</b> (ID: {user_house_id}) • Meter Serial: <b>{details.get('meterId', 'METER_101')}</b> • Pulse Telemetry: <b>Live</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 5 KPI Cards for Resident
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric(label="Today's Usage", value=f"{details.get('todayUsageLitres', 280):,.0f} L", delta=f"{details.get('percentageChange', 0):+.1f}% vs avg")
    with k2:
        st.metric(label="Monthly Volume", value=f"{details.get('monthlyUsageLitres', 7200):,.0f} L")
    with k3:
        st.metric(label="Current Invoice", value=f"₹{latest_bill.get('totalAmount', 920):,.2f}")
    with k4:
        st_val = latest_bill.get("paymentStatus", "PENDING")
        st.metric(label="Bill Status", value=st_val, delta="Due 10th Oct" if st_val == "PENDING" else "Settled")
    with k5:
        anom_st = details.get("anomalyStatus", "NORMAL")
        st.metric(label="Telemetry State", value=anom_st, delta="Check Fixtures" if anom_st == "ABNORMAL" else "Eco-Optimal", delta_color="inverse" if anom_st == "ABNORMAL" else "normal")

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 5 Major Charts for Resident
    st.markdown("<h3 style='color: #00F0FF; font-weight: 700; margin-bottom: 14px;'>Personal Water Consumption Telemetry</h3>", unsafe_allow_html=True)

    # Chart 1: Daily Usage & Chart 2: Hourly Usage Today
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_daily_consumption(daily_cons), use_container_width=True)
    with c2:
        st.plotly_chart(chart_hourly_profile(hourly_cons), use_container_width=True)

    # Chart 3: Weekly Usage & Chart 4: Monthly Usage
    c3, c4 = st.columns(2)
    with c3:
        df_w = pd.DataFrame(weekly_cons)
        fig_w = go.Figure(go.Bar(
            x=df_w["label"], y=df_w["litres"],
            marker_color="#6366F1",
            hovertemplate='%{x}<br>Consumed: <b>%{y:,.0f} L</b><extra></extra>'
        ))
        fig_w.update_yaxes(title_text="Litres")
        st.plotly_chart(format_plotly_chart(fig_w, "Chart 3: Weekly Consumption Trend", height=290), use_container_width=True)

    with c4:
        df_m = pd.DataFrame(monthly_cons)
        fig_m = go.Figure(go.Bar(
            x=df_m["label"], y=df_m["litres"],
            marker_color=PRIMARY_AQUA,
            hovertemplate='%{x}<br>Monthly: <b>%{y:,.0f} L</b><extra></extra>'
        ))
        fig_m.update_yaxes(title_text="Litres")
        st.plotly_chart(format_plotly_chart(fig_m, "Chart 4: 6-Month Water Usage History", height=290), use_container_width=True)

    # Chart 5: Usage vs Apartment Average Comparison
    st.markdown("<h4 style='color: #00F0FF; font-weight: 700; margin-top: 16px;'>Chart 5: Your Flat vs Building Average Consumption</h4>", unsafe_allow_html=True)
    comp_labels = ["Your Flat Today", "Apartment Average Today", "Your Daily Baseline"]
    comp_values = [details.get("todayUsageLitres", 280), details.get("apartmentAverageToday", 310), details.get("averageDailyLitres", 290)]
    fig_comp = go.Figure(go.Bar(
        x=comp_labels, y=comp_values,
        marker_color=[PRIMARY_AQUA, "#6366F1", SUCCESS_TEAL],
        hovertemplate='%{x}: <b>%{y:,.0f} Litres</b><extra></extra>'
    ))
    fig_comp.update_yaxes(title_text="Consumption (Litres)")
    st.plotly_chart(format_plotly_chart(fig_comp, "Comparison with Building Average", height=300), use_container_width=True)

    # -------------------------------------------------------------
    # RESIDENT ECO-RANK SCORECARD & LEAK INSPECTION WIZARD
    # -------------------------------------------------------------
    st.markdown("<h3 style='color: #00F0FF; font-weight: 700; margin-top: 28px; margin-bottom: 14px;'>🌱 Resident Eco-Scorecard & Leak Self-Inspection Wizard</h3>", unsafe_allow_html=True)

    e1, e2 = st.columns(2)
    with e1:
        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border};">
            <div class="aq-card-header">
                <span>🏆 Community Water Conservation Leaderboard</span>
                <span class="badge-live" style="background: rgba(16,185,129,0.2); color: #10B981;">Gold Rank</span>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; color: {text_sub};">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Apartment Profile</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">{user_house_id} of {len(RESIDENT_PROFILES)} Flats</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Daily Use vs Community Average</b></td><td style="text-align: right; color: #00F0FF; font-weight: 700;">{abs(usage_difference):,.0f} L/day {difference_direction}</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Estimated Monthly Cost Difference</b></td><td style="text-align: right; color: #10B981; font-weight: 700;">₹ {monthly_difference * 0.10:,.2f} {difference_direction}</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Shower Duration Avg</b></td><td style="text-align: right; color: {text_main};">6.2 mins (Eco-Standard: &lt; 7 mins)</td></tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Pulse Sensor Status</b></td><td style="text-align: right; color: #10B981; font-weight: 600;">Active (Battery 3.6V)</td></tr>
                <tr><td style="padding: 8px 0;"><b>Resident Eco Badge</b></td><td style="text-align: right; color: {DANGER_CORAL if telemetry_status == 'ABNORMAL' else SUCCESS_TEAL}; font-weight: 700;">{'⚠ Usage Review' if telemetry_status == 'ABNORMAL' else '✓ Usage Normal'}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with e2:
        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border};">
            <div class="aq-card-header">
                <span>🔍 In-Home Leak Self-Inspection Checklist</span>
                <span class="badge-live">DIY Guide</span>
            </div>
            <div style="font-size: 0.88rem; color: {text_sub}; line-height: 1.6;">
                <div style="margin-bottom: 8px;"><b>🚽 Toilet Cistern Test:</b> Put 3 drops of food coloring into the cistern tank. If color appears in the bowl within 15 minutes without flushing, replace the rubber flapper.</div>
                <div style="margin-bottom: 8px;"><b>🚿 Shower & Faucet Aerators:</b> Unscrew aerator nozzles every 3 months to clear mineral sediment and ensure smooth, splash-free flow.</div>
                <div style="margin-bottom: 8px;"><b>🧺 Washing Machine Inlets:</b> Inspect rubber braided hoses behind your machine for micro-tears or moisture buildup.</div>
                <div><b>🚰 RO Purifier Reject Line:</b> Route reject water to a bucket for plant watering and floor cleaning.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Bill Section & Payment
    st.markdown("<h3 style='color: #00F0FF; font-weight: 700; margin-top: 28px; margin-bottom: 14px;'>Current Invoice & Payment Breakdown</h3>", unsafe_allow_html=True)
    b_col1, b_col2 = st.columns([1.5, 1])

    with b_col1:
        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border};">
            <div class="aq-card-header">
                <span>Invoice #{latest_bill.get('id', 'BILL-SEP-2026')}</span>
                <span class="{'badge-live' if latest_bill.get('paymentStatus') == 'PAID' else 'badge-critical'}">{latest_bill.get('paymentStatus', 'PENDING')}</span>
            </div>
            <div style="line-height: 2.0; font-size: 0.92rem; color: {text_sub};">
                • Billing Period: <b style="color: {text_main};">{latest_bill.get('billingPeriod', '2026-09')}</b><br>
                • Recorded Consumption: <b style="color: #00F0FF;">{latest_bill.get('consumptionLitres', 7200):,.0f} Litres</b><br>
                • Volumetric Tariff: <b style="color: {text_main};">₹{latest_bill.get('waterRate', 0.10):.2f} / Litre</b><br>
                • Water Usage Charge: <b style="color: {text_main};">₹{latest_bill.get('waterCharge', 720):,.2f}</b><br>
                • Fixed Apartment Infrastructure Charge: <b style="color: {text_main};">₹{latest_bill.get('fixedCharge', 200):,.2f}</b><br>
                <hr style="margin: 10px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 1.25rem; font-weight: 800; color: #10B981;">
                    Total Payable Amount: ₹{latest_bill.get('totalAmount', 920):,.2f}
                </div>
                <div style="font-size: 0.85rem; color: #A5B4FC; margin-bottom: 12px;">Due Date: {latest_bill.get('dueDate', '2026-10-10')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Resident bill export
        df_res_bill = pd.DataFrame([latest_bill])
        st.markdown(create_html_csv_download_button(
            df_res_bill,
            f"aquanest_bill_{user_house_id}_{latest_bill.get('billingPeriod', 'latest')}.csv",
            "📥 Download My Bill Invoice (CSV)",
            is_primary=True
        ), unsafe_allow_html=True)


    with b_col2:
        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border}; text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 8px;">💳</div>
            <h4 style="color: {text_main}; font-weight: 700;">Digital Water Payment</h4>
            <p style="color: {text_sub}; font-size: 0.88rem;">Instant payment settlement via UPI / NetBanking simulator</p>
        """, unsafe_allow_html=True)

        if latest_bill.get("paymentStatus") == "PENDING":
            if st.button("💳 Pay Invoice Now (₹" + str(latest_bill.get('totalAmount', 920)) + ")", key="pay_now_btn", use_container_width=True):
                api_client.update_payment(latest_bill.get("id"), "PAID")
                st.success("✅ Payment processed successfully! Digital receipt issued.")
                st.rerun()
        else:
            st.success("✅ Invoice for this billing cycle is fully settled.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Flat Alerts and AI Recommendations
    st.markdown("<h3 style='color: #00F0FF; font-weight: 700; margin-top: 24px; margin-bottom: 14px;'>Personalized Water-Saving Advice & Alerts</h3>", unsafe_allow_html=True)
    a_col, r_col = st.columns(2)

    with a_col:
        st.markdown("<b>Apartment Unit Alerts</b>", unsafe_allow_html=True)
        flat_alerts = [a for a in alerts if a.get("houseId") in [user_house_id, "ALL"]]
        for a in flat_alerts[:3]:
            st.markdown(f"""
            <div style="background: {card_bg}; border-left: 4px solid #F59E0B; border: 1px solid {card_border}; border-left-width: 4px; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px; font-size: 0.88rem; color: {text_sub};">
                <b style="color: #F59E0B;">{a.get('type')}</b>: {a.get('message')}
            </div>
            """, unsafe_allow_html=True)

    with r_col:
        st.markdown("<b>AI Conservation Recommendations</b>", unsafe_allow_html=True)
        for r in recs[:3]:
            st.markdown(f"""
            <div style="background: {card_bg}; border-left: 4px solid #00F0FF; border: 1px solid {card_border}; border-left-width: 4px; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px; font-size: 0.88rem; color: {text_sub};">
                <b style="color: #00F0FF;">{r.get('title')}</b>: {r.get('message')}
            </div>
            """, unsafe_allow_html=True)
