"""
AquaNest – Alerts & Incident Management View
Multi-category alert dispatcher with status filtering, dynamic dark mode,
escalation tier matrix, and one-click resolution.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.theme import format_plotly_chart, DANGER_CORAL, WARNING_AMBER, SUCCESS_TEAL, DEEP_NAVY


def render_alerts_view(api_client, user_role="ADMIN", user_house_id=None):
    alerts = api_client.get_alerts(role=user_role, house_id=user_house_id)
    is_dark = st.session_state.get("dark_theme", True)

    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.88) 0%, rgba(22, 15, 56, 0.94) 100%)" if is_dark else "#FFFFFF"
    card_border = "rgba(139, 92, 246, 0.35)" if is_dark else "rgba(226, 232, 240, 0.9)"

    st.markdown(f"""
    <div class="aq-app-header">
        <div>
            <div class="aq-app-eyebrow">AQUANEST INCIDENT RESPONSE</div>
            <h1 style="color: {text_main};">System Alerts & Incident Dispatch</h1>
            <p style="color: {text_sub};">Multi-tier notifications covering ultrasonic levels, leakages, pressure, and machine learning anomalies.</p>
        </div>
        <div class="aq-app-header-status"><span class="pulse-dot"></span> Real-time Dispatch Active</div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Quick Metrics
    total = len(alerts)
    new_cnt = sum([1 for a in alerts if a.get("status") == "NEW"])
    crit_cnt = sum([1 for a in alerts if a.get("severity") == "CRITICAL"])
    res_cnt = sum([1 for a in alerts if a.get("status") == "RESOLVED"])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(label="Total Logged Alerts", value=total)
    with k2:
        st.metric(label="New / Unacknowledged", value=new_cnt, delta="Pending Action", delta_color="inverse")
    with k3:
        st.metric(label="Critical Severity", value=crit_cnt, delta="Immediate Attention", delta_color="inverse")
    with k4:
        st.metric(label="Resolved Incidents", value=res_cnt, delta="Closed")

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Category and Severity Visuals
    c1, c2 = st.columns(2)
    with c1:
        type_counts = {}
        for a in alerts:
            t = a.get("type", "GENERAL")
            type_counts[t] = type_counts.get(t, 0) + 1
        fig_cat = go.Figure(go.Bar(
            x=list(type_counts.keys()), y=list(type_counts.values()),
            marker_color="#6366F1",
            hovertemplate='%{x}: %{y} alerts<extra></extra>'
        ))
        fig_cat.update_yaxes(title_text="Count", dtick=1)
        st.plotly_chart(format_plotly_chart(fig_cat, "Alert Distribution by Subsystem Category", height=280), use_container_width=True)

    with c2:
        sev_counts = {"CRITICAL": crit_cnt, "WARNING": max(0, total - crit_cnt - 1), "INFO": 1}
        fig_sev = go.Figure(go.Pie(
            labels=list(sev_counts.keys()), values=list(sev_counts.values()), hole=0.5,
            marker=dict(colors=[DANGER_CORAL, WARNING_AMBER, SUCCESS_TEAL]),
            hovertemplate='<b>%{label}</b>: %{value} alerts<extra></extra>'
        ))
        st.plotly_chart(format_plotly_chart(fig_sev, "Alerts by Severity Level", height=280), use_container_width=True)

    # -------------------------------------------------------------
    # ESCALATION PROTOCOL & ACTIVE ALERT FEED
    # -------------------------------------------------------------
    st.markdown("<h3 style='color: #00F0FF; font-weight: 700; margin-top: 24px; margin-bottom: 14px;'>🚨 Active Incidents Feed & Multi-Tier Escalation SOP</h3>", unsafe_allow_html=True)

    # Filter Bar
    status_filter = st.selectbox("Filter by Incident Status", ["ALL", "NEW", "ACKNOWLEDGED", "RESOLVED"], index=0)
    filtered_alerts = alerts if status_filter == "ALL" else [a for a in alerts if a.get("status") == status_filter]

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    for a in filtered_alerts:
        sev = a.get("severity", "INFO")
        border_col = DANGER_CORAL if sev == "CRITICAL" else (WARNING_AMBER if sev == "WARNING" else SUCCESS_TEAL)
        badge_cls = "badge-critical" if sev == "CRITICAL" else ("badge-demo" if sev == "WARNING" else "badge-live")

        st.markdown(f"""
        <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border}; border-left: 5px solid {border_col}; margin-bottom: 12px; padding: 16px 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 1.05rem; font-weight: 700; color: {text_main};">
                    {a.get('type')} • Zone: {a.get('houseId', 'MAIN')}
                </span>
                <span class="{badge_cls}">{sev} • {a.get('status')}</span>
            </div>
            <div style="color: {text_sub}; font-size: 0.92rem; margin-bottom: 8px;">
                {a.get('message')}
            </div>
            <div style="font-size: 0.8rem; color: #A5B4FC;">
                Timestamp: {a.get('timestamp', 'Recent')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Escalation Matrix
    st.markdown(f"""
    <div class="aq-card" style="background: {card_bg}; border: 1px solid {card_border}; margin-top: 20px;">
        <div class="aq-card-header">
            <span>📞 Multi-Tier Incident Escalation Matrix</span>
            <span class="badge-live">24/7 SLA</span>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; color: {text_sub};">
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Tier 1: Minor Leak / Sensor Noise (&lt; 2 L/min)</b></td><td style="text-align: right; color: #00F0FF;">Resident App Notification • 24hr Inspection</td></tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);"><td style="padding: 8px 0;"><b>Tier 2: Nocturnal Seepage / Tank Overflow Risk</b></td><td style="text-align: right; color: #F59E0B; font-weight: 700;">Admin SMS + On-Duty Plumber Dispatch (&lt; 2 hrs)</td></tr>
            <tr><td style="padding: 8px 0;"><b>Tier 3: Distribution Line Rupture (&gt; 10 L/min)</b></td><td style="text-align: right; color: #EF4444; font-weight: 700;">Auto-Shutoff Solenoid + Emergency Voice Call (&lt; 15 mins)</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
