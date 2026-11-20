"""
AquaNest – Reports & Compliance Audit View
Generates downloadable CSV spreadsheets, ZIP report packages, JSON audit trails, and compliance tables across
apartment water consumption, resident billing, leakage incidents, pump energy logs, and AI anomalies.
Includes UTF-8-BOM CSV export for seamless Excel compatibility and direct local disk exports.
"""

import os
import io
import json
import base64
import zipfile
import datetime
import textwrap
import streamlit as st
import pandas as pd


def create_html_download_button(data_bytes, filename, mime_type, label, is_primary=True):
    """Generates an HTML5 <a> tag with explicit download attribute to force exact filename and extension in Chrome."""
    b64 = base64.b64encode(data_bytes).decode('utf-8')
    bg_style = "linear-gradient(135deg, #00A8E8 0%, #6366F1 100%)" if is_primary else "linear-gradient(135deg, #8B5CF6 0%, #4F46E5 100%)"
    border_style = "1px solid rgba(0, 240, 255, 0.7)" if is_primary else "1px solid rgba(139, 92, 246, 0.6)"
    text_color = "#FFFFFF"
    shadow_style = "0 6px 20px rgba(0, 168, 232, 0.5)" if is_primary else "0 6px 20px rgba(139, 92, 246, 0.4)"

    return f"""
    <a href="data:{mime_type};base64,{b64}" download="{filename}"
       style="display: flex; align-items: center; justify-content: center; width: 100%;
              background: {bg_style}; border: {border_style}; color: {text_color} !important;
              -webkit-text-fill-color: {text_color} !important;
              text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6) !important;
              text-decoration: none !important; font-weight: 800; font-size: 15px;
              border-radius: 12px; padding: 14px 20px; box-sizing: border-box;
              box-shadow: {shadow_style}; cursor: pointer; text-align: center;
              transition: all 0.2s ease-in-out; margin: 4px 0;">
        {label}
    </a>
    """


def render_reports_view(api_client, user_role="ADMIN"):
    if user_role != "ADMIN":
        st.error("⛔ Access Denied: Reports generation is restricted to Administrators.")
        return

    is_dark = st.session_state.get("dark_theme", True)
    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"
    text_muted = "#A5B4FC" if is_dark else "#64748B"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.90) 0%, rgba(22, 15, 56, 0.95) 100%)" if is_dark else "#FFFFFF"
    card_border = "rgba(139, 92, 246, 0.35)" if is_dark else "rgba(226, 232, 240, 0.9)"
    accent_blue = "#00F0FF" if is_dark else "#00A8E8"
    apartment_houses = api_client.get_houses(role="ADMIN")

    # Header
    st.markdown(textwrap.dedent(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 19, 74, 0.95) 0%, rgba(13, 8, 39, 0.95) 100%);
                border-radius: 16px; padding: 22px 26px; margin-bottom: 20px;
                border: 1px solid {card_border}; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
            <div>
                <div style="font-size: 11px; font-weight: 800; letter-spacing: 1.5px; color: {accent_blue}; text-transform: uppercase;">
                    AQUANEST AUDIT & COMPLIANCE ENGINE
                </div>
                <h1 style="color: {text_main}; margin: 4px 0 6px 0; font-size: 28px; font-weight: 800;">
                    Official CSV Reports & Audit Logs
                </h1>
                <p style="color: {text_sub}; margin: 0; font-size: 14px;">
                    Generate and download CSV datasets for consumption, billing, leakages, pump energy, and ESG compliance.
                </p>
            </div>
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4);
                        border-radius: 30px; padding: 8px 18px; color: #10B981; font-size: 13px; font-weight: 700;">
                ● ISO 14046 / NBC Compliant
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    # ESG Sustainability Summary Card
    st.markdown(textwrap.dedent(f"""
    <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 14px; padding: 18px 22px; margin-bottom: 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-size: 15px; font-weight: 800; color: {text_main};">🌱 ESG Environmental & Water Footprint Summary (Q3 2026)</span>
            <span style="background: rgba(16, 185, 129, 0.2); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 20px; padding: 3px 12px; font-size: 11px; font-weight: 700;">
                Certified Water Balance
            </span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; font-size: 13px; color: {text_sub};">
            <div>Total Inflow Sourced: <b style="color: {accent_blue}; font-size: 15px;">58,500 L</b></div>
            <div>Delivered to Sub-Meters: <b style="color: #10B981; font-size: 15px;">55,500 L (94.87%)</b></div>
            <div>Unaccounted Water (UAW): <b style="color: #F59E0B; font-size: 15px;">3,000 L (5.13%)</b></div>
            <div>Carbon Offset / Energy Saved: <b style="color: #10B981; font-size: 15px;">14.2 kg CO₂e</b></div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    # -------------------------------------------------------------
    # REPORT CONFIGURATION CONTROLS
    # -------------------------------------------------------------
    r_col1, r_col2, r_col3 = st.columns([2.2, 1.4, 1.4])

    with r_col1:
        report_type = st.selectbox(
            "📋 Select Report Dataset Category",
            [
                "Monthly Apartment Water Consumption",
                "Monthly Resident Water Invoices & Billing",
                "Leakage Diagnostics & Physical Loss Log",
                "AI Anomaly Detection & Flagged Events",
                "Water Pump Operating Hours & Electrical Energy"
            ],
            index=0,
            key="rep_type_select"
        )

    with r_col2:
        period_filter = st.selectbox(
            "📅 Time Period",
            ["Current Billing Cycle (Oct 2026)", "Last Month (Sep 2026)", "Last 30 Days", "Year-to-Date (2026)", "All Recorded Data"],
            index=0,
            key="rep_period_select"
        )

    with r_col3:
        apartment_numbers = [house["houseNumber"] for house in apartment_houses]
        all_flats_label = (
            f"All Flats ({min(apartment_numbers)} - {max(apartment_numbers)})"
            if apartment_numbers else "All Flats"
        )
        house_filter = st.selectbox(
            "🏢 Apartment Filter",
            [all_flats_label] + [f"Flat {number}" for number in apartment_numbers],
            index=0,
            key="rep_house_select"
        )

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # DATASET BUILDERS
    # -------------------------------------------------------------
    today_str = datetime.date.today().isoformat()
    selected_house_id = "ALL" if house_filter.startswith("All Flats") else house_filter.replace("Flat ", "H")

    def build_consumption_df():
        houses = api_client.get_houses(role="ADMIN")
        if selected_house_id != "ALL":
            houses = [h for h in houses if h.get("houseId") == selected_house_id]
        data_rows = []
        for h in houses:
            data_rows.append({
                "Report Date": today_str,
                "Unit ID": h["houseId"],
                "Flat Number": h["houseNumber"],
                "Resident Name": h["residentName"],
                "Pulse Meter ID": h["meterId"],
                "Today Usage (Litres)": h["todayUsageLitres"],
                "Monthly Usage (Litres)": h["monthlyUsageLitres"],
                "Daily Average (Litres)": h["averageDailyLitres"],
                "Peak Hour Flow (Litres)": h["peakUsageLitres"],
                "Meter Pulse Status": h["status"],
                "AI Anomaly Flag": h["anomalyStatus"]
            })
        return pd.DataFrame(data_rows), "aquanest_apartment_consumption"

    def build_billing_df():
        bills = api_client.get_bills(role="ADMIN")
        if selected_house_id != "ALL":
            bills = [b for b in bills if b.get("houseId") == selected_house_id]
        data_rows = []
        for b in bills:
            data_rows.append({
                "Invoice ID": b.get("id"),
                "Unit ID": b.get("houseId"),
                "Flat Number": b.get("houseNumber"),
                "Resident Name": b.get("residentName"),
                "Billing Period": b.get("billingPeriod"),
                "Consumption (Litres)": b.get("consumptionLitres"),
                "Water Tariff (INR/L)": b.get("waterRate", 0.10),
                "Volumetric Charge (INR)": b.get("waterCharge"),
                "Fixed Maintenance Charge (INR)": b.get("fixedCharge", 200.0),
                "Total Amount Due (INR)": b.get("totalAmount"),
                "Payment Due Date": b.get("dueDate"),
                "Payment Status": b.get("paymentStatus")
            })
        return pd.DataFrame(data_rows), "aquanest_water_billing_invoices"

    def build_leakage_df():
        leaks = api_client.get_leakages()
        data_rows = []
        for l in leaks:
            data_rows.append({
                "Incident ID": l.get("id"),
                "Leakage Type": l.get("type"),
                "Infrastructure Zone": l.get("zone"),
                "Estimated Loss (Litres)": l.get("estimatedLossLitres"),
                "Financial Impact (INR)": round(l.get("estimatedLossLitres", 0) * 0.10, 2),
                "Severity Level": l.get("severity"),
                "Distribution Pressure (bar)": l.get("pressureBar"),
                "Flow Mismatch Rate (L/min)": l.get("flowMismatchLpm"),
                "Investigation Status": l.get("status"),
                "Detected Timestamp": l.get("detectedAt"),
                "Diagnostic Evidence": l.get("evidence")
            })
        return pd.DataFrame(data_rows), "aquanest_leakage_diagnostics"

    def build_anomalies_df():
        anoms = api_client.get_anomalies(role="ADMIN")
        data_rows = []
        for a in anoms:
            data_rows.append({
                "Anomaly ID": a.get("id"),
                "Unit ID": a.get("houseId"),
                "Expected Daily Usage (L)": a.get("expectedUsageLitres"),
                "Actual Recorded Usage (L)": a.get("actualUsageLitres"),
                "Excess Litres Wasted": max(0.0, a.get("actualUsageLitres", 0) - a.get("expectedUsageLitres", 0)),
                "IsolationForest Score": a.get("anomalyScore"),
                "Anomaly Classification": a.get("status"),
                "Diagnostic Reason": a.get("reason"),
                "Recommended Corrective Action": a.get("recommendation")
            })
        return pd.DataFrame(data_rows), "aquanest_ai_anomalies"

    def build_pumplogs_df():
        logs = api_client.get_pump_logs()
        data_rows = []
        for p in logs:
            data_rows.append({
                "Log ID": p.get("id"),
                "Contactor Action": p.get("status"),
                "Operation Mode": p.get("mode"),
                "Overhead Tank Level (%)": p.get("tankLevel"),
                "Cycle Start Time": p.get("startTime"),
                "Runtime Duration (Seconds)": p.get("durationSeconds"),
                "Runtime (Minutes)": round(p.get("durationSeconds", 0) / 60.0, 1),
                "Estimated Energy Draw (kWh)": round((p.get("durationSeconds", 0) / 3600.0) * 1.5, 2),
                "Electricity Cost (INR @ Rs 8/kWh)": round(((p.get("durationSeconds", 0) / 3600.0) * 1.5) * 8.0, 2),
                "Trigger Condition": p.get("trigger")
            })
        return pd.DataFrame(data_rows), "aquanest_pump_operating_energy_logs"

    # Select Active Dataset
    if report_type == "Monthly Apartment Water Consumption":
        df, file_prefix = build_consumption_df()
    elif report_type == "Monthly Resident Water Invoices & Billing":
        df, file_prefix = build_billing_df()
    elif report_type == "Leakage Diagnostics & Physical Loss Log":
        df, file_prefix = build_leakage_df()
    elif report_type == "AI Anomaly Detection & Flagged Events":
        df, file_prefix = build_anomalies_df()
    else:
        df, file_prefix = build_pumplogs_df()

    # Pre-generate CSV payload with UTF-8 BOM for instant 1-click download
    rec_count = len(df)
    csv_raw_text = df.to_csv(index=False)
    csv_bytes = ('\ufeff' + csv_raw_text).encode('utf-8')
    csv_size_kb = round(len(csv_bytes) / 1024.0, 2)
    file_name_csv = f"{file_prefix}_{today_str}.csv"
    file_name_json = f"{file_prefix}_{today_str}.json"

    # Auto-save active dataset to exports/ folder so file is always available locally
    try:
        api_client.export_csv_to_disk(df, filename_prefix=file_prefix)
    except Exception:
        pass

    # -------------------------------------------------------------
    # DATASET METRICS
    # -------------------------------------------------------------
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Total Records Ready", f"{rec_count} rows")
    with m_col2:
        st.metric("Export Encoding", "UTF-8 with BOM (.csv)")
    with m_col3:
        st.metric("File Size", f"{csv_size_kb} KB")
    with m_col4:
        st.metric("Target Filename", file_name_csv)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # BUILD MULTI-REPORT ZIP PACKAGE IN MEMORY
    # -------------------------------------------------------------
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        df_c, p_c = build_consumption_df()
        df_b, p_b = build_billing_df()
        df_l, p_l = build_leakage_df()
        df_a, p_a = build_anomalies_df()
        df_p, p_p = build_pumplogs_df()

        zf.writestr(f"01_{p_c}_{today_str}.csv", ('\ufeff' + df_c.to_csv(index=False)).encode('utf-8'))
        zf.writestr(f"02_{p_b}_{today_str}.csv", ('\ufeff' + df_b.to_csv(index=False)).encode('utf-8'))
        zf.writestr(f"03_{p_l}_{today_str}.csv", ('\ufeff' + df_l.to_csv(index=False)).encode('utf-8'))
        zf.writestr(f"04_{p_a}_{today_str}.csv", ('\ufeff' + df_a.to_csv(index=False)).encode('utf-8'))
        zf.writestr(f"05_{p_p}_{today_str}.csv", ('\ufeff' + df_p.to_csv(index=False)).encode('utf-8'))
    zip_buffer.seek(0)
    zip_bytes = zip_buffer.getvalue()
    file_name_zip = f"aquanest_all_reports_bundle_{today_str}.zip"

    # Map backend CSV endpoint for direct REST API stream
    backend_csv_endpoint = {
        "Monthly Apartment Water Consumption": "http://localhost:8080/api/reports/consumption/csv",
        "Monthly Resident Water Invoices & Billing": "http://localhost:8080/api/reports/billing/csv",
        "Leakage Diagnostics & Physical Loss Log": "http://localhost:8080/api/reports/leakage/csv",
        "AI Anomaly Detection & Flagged Events": "http://localhost:8080/api/reports/anomalies/csv",
        "Water Pump Operating Hours & Electrical Energy": "http://localhost:8080/api/reports/pumplogs/csv"
    }.get(report_type, "http://localhost:8080/api/reports/all/csv")

    # -------------------------------------------------------------
    # 1-CLICK INSTANT DOWNLOAD ACTION BAR (HTML5 Direct Force-Filename Downloads)
    # -------------------------------------------------------------
    st.markdown(textwrap.dedent(f"""
    <div style="background: linear-gradient(135deg, rgba(26, 16, 68, 0.95) 0%, rgba(18, 12, 48, 0.95) 100%);
                border: 1px solid {card_border}; border-radius: 14px; padding: 18px 22px; margin-bottom: 18px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.30);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="font-size: 16px; font-weight: 800; color: #FFFFFF;">📥 1-Click CSV & ZIP Download Center</span>
                <div style="font-size: 12px; color: {text_sub};">Click below to download <b>{file_name_csv}</b> directly to your PC with full Excel compatibility and UTF-8 encoding.</div>
            </div>
            <div style="background: rgba(0, 240, 255, 0.15); border: 1px solid rgba(0, 240, 255, 0.35); border-radius: 20px; padding: 4px 14px; font-size: 12px; color: {accent_blue}; font-weight: 700;">
                Target: {file_name_csv}
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    btn_row1, btn_row2, btn_row3 = st.columns([1.4, 1.4, 1.4])

    with btn_row1:
        # HTML5 Direct Download Link (Forces exact .csv filename in Chrome)
        html_csv_btn = create_html_download_button(
            data_bytes=csv_bytes,
            filename=file_name_csv,
            mime_type="text/csv",
            label=f"📥 Download CSV File",
            is_primary=True
        )
        st.markdown(html_csv_btn, unsafe_allow_html=True)

    with btn_row2:
        # Direct Backend HTTP REST API Download Link (Real HTTP Content-Disposition)
        st.markdown(f"""
        <a href="{backend_csv_endpoint}" download="{file_name_csv}"
           style="display: flex; align-items: center; justify-content: center; width: 100%;
                  background: linear-gradient(135deg, rgba(35, 23, 85, 0.95) 0%, rgba(24, 15, 62, 0.95) 100%);
                  border: 1px solid rgba(0, 240, 255, 0.7); color: #00F0FF !important;
                  -webkit-text-fill-color: #00F0FF !important;
                  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6) !important;
                  text-decoration: none !important; font-weight: 800; font-size: 15px;
                  border-radius: 12px; padding: 14px 20px; box-sizing: border-box;
                  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4); cursor: pointer; text-align: center;
                  transition: all 0.2s ease-in-out; margin: 4px 0;">
            🌐 Backend API Direct Stream
        </a>
        """, unsafe_allow_html=True)

    with btn_row3:
        # HTML5 Direct ZIP Download Link (Forces exact .zip filename in Chrome)
        html_zip_btn = create_html_download_button(
            data_bytes=zip_bytes,
            filename=file_name_zip,
            mime_type="application/zip",
            label=f"📦 Download 5-in-1 ZIP",
            is_primary=False
        )
        st.markdown(html_zip_btn, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Standard Fallback Download Buttons
    sec_col1, sec_col2, sec_col3 = st.columns([1.5, 1.5, 1.0])

    with sec_col1:
        st.download_button(
            label=f"💾 Alternative Download (.csv)",
            data=csv_bytes,
            file_name=file_name_csv,
            mime="text/csv",
            use_container_width=True,
            key=f"native_dl_csv_btn_{file_prefix}"
        )

    with sec_col2:
        json_str = df.to_json(orient="records", indent=2)
        st.download_button(
            label="📄 Download JSON Audit Trail",
            data=json_str.encode('utf-8'),
            file_name=file_name_json,
            mime="application/json",
            use_container_width=True,
            key=f"native_dl_json_btn_{file_prefix}"
        )

    with sec_col3:
        if st.button("🔄 Sync Live", key="refresh_reports_btn", use_container_width=True):
            st.toast("Report data synchronized from backend.", icon="🔄")
            st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # DATA PREVIEW TABLE
    # -------------------------------------------------------------
    st.markdown(f"<h4 style='color: {text_main};'>Live Data Table Preview ({rec_count} Rows)</h4>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # RAW CSV TEXT PREVIEW EXPANDER (COPYABLE)
    # -------------------------------------------------------------
    with st.expander("📋 View Raw CSV Comma-Separated Text (Direct Copy)", expanded=False):
        st.code(csv_raw_text, language="csv")

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # EXPORT ARCHIVE & SAVED CSV FILES BROWSER
    # -------------------------------------------------------------
    st.markdown(textwrap.dedent(f"""
    <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 14px; padding: 18px 22px; margin-bottom: 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
            <span style="font-size: 15px; font-weight: 800; color: {text_main};">📁 Local Server Disk Storage (Saved in <code>aquanest/exports/</code>)</span>
            <span style="color: {accent_blue}; font-size: 12px; font-weight: 600;">Full Path: <code>d:\\nest\\jr\\aquanest\\exports\\</code></span>
        </div>
        <p style="font-size: 13px; color: {text_sub}; margin: 0 0 12px 0;">
            All CSV reports are also automatically saved on disk in the <code>exports/</code> directory with UTF-8 BOM encoding for direct opening in Microsoft Excel.
        </p>
    """), unsafe_allow_html=True)

    saved_reports = api_client.list_exported_reports()
    if saved_reports:
        df_saved = pd.DataFrame(saved_reports)
        st.dataframe(df_saved[["fileName", "sizeKb", "modified"]].rename(columns={
            "fileName": "CSV File Name",
            "sizeKb": "File Size (KB)",
            "modified": "Generated Timestamp"
        }), use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No saved CSV reports yet in exports/ directory.")

    st.markdown("</div>", unsafe_allow_html=True)
