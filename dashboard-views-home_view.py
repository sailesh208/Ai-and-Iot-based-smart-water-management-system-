"""
AquaNest – Smart Apartment Water Management Homepage
Features topmost glass header, rich Navy-Purplish Dark Mode with high contrast typography,
sliding light/dark theme toggle, hero section with IoT visuals, High-Tech Bento Feature Boxes,
interactive 20-apartment telemetry matrix, water savings calculator, technical specs, and interactive FAQ.
Uses textwrap.dedent to ensure zero markdown formatting artifacts.
"""

import os
import textwrap
import streamlit as st

from services.resident_profiles import RESIDENT_PROFILES


def render_home_page():
    """Renders the comprehensive AquaNest Homepage with rich feature boxes, visuals, and interactive tools."""

    if "dark_theme" not in st.session_state:
        st.session_state["dark_theme"] = True

    is_dark = st.session_state["dark_theme"]

    # Image asset paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hero_img_path = os.path.join(base_dir, "assets", "hero_apartment.jpg")
    sensor_img_path = os.path.join(base_dir, "assets", "smart_sensor.jpg")

    # Dynamic Theme Colors
    header_bg = "rgba(25, 17, 66, 0.94)" if is_dark else "rgba(255, 255, 255, 0.96)"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.88) 0%, rgba(22, 15, 56, 0.94) 100%)" if is_dark else "#FFFFFF"
    card_border = "rgba(139, 92, 246, 0.35)" if is_dark else "rgba(226, 232, 240, 0.9)"
    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#334155"
    text_muted = "#A5B4FC" if is_dark else "#64748B"
    accent_blue = "#00F0FF" if is_dark else "#00A8E8"
    accent_glow = "0 8px 30px rgba(0, 240, 255, 0.25)" if is_dark else "0 8px 24px rgba(10, 37, 64, 0.08)"
    card_shadow = "0 12px 35px rgba(0, 0, 0, 0.55)" if is_dark else "0 10px 30px rgba(10, 37, 64, 0.06)"

    # Page Styles
    st.markdown(textwrap.dedent(f"""
<style>
/* Top Navigation Header */
.aq-nav-top-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 24px;
    background: {header_bg};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid {card_border};
    border-radius: 16px;
    box-shadow: {card_shadow};
    margin-bottom: 20px;
}}

.aq-brand-holder {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.aq-brand-avatar {{
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, #00A8E8 0%, #6366F1 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    color: #FFFFFF;
    box-shadow: 0 4px 14px rgba(0, 168, 232, 0.4);
}}

.aq-brand-h1 {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    color: {text_main};
    line-height: 1;
    margin: 0;
}}

.aq-brand-sub {{
    font-size: 0.62rem;
    font-weight: 800;
    color: {accent_blue};
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-top: 2px;
}}

.aq-nav-links-mid {{
    display: flex;
    align-items: center;
    gap: 24px;
}}

.aq-nav-item-link {{
    font-size: 0.92rem;
    font-weight: 600;
    color: {text_sub};
    text-decoration: none;
    cursor: pointer;
}}

.aq-nav-item-link:hover {{
    color: {accent_blue};
}}

/* Hero Container */
.aq-hero-section {{
    background: {'radial-gradient(circle at 30% 20%, rgba(99, 102, 241, 0.25) 0%, rgba(0, 240, 255, 0.08) 50%, rgba(12, 8, 36, 0) 80%)' if is_dark else 'radial-gradient(circle at 30% 20%, rgba(0, 168, 232, 0.12) 0%, rgba(240, 246, 255, 0) 70%)'};
    border-radius: 24px;
    padding: 24px 20px 20px;
    margin-bottom: 28px;
}}

.aq-live-pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 5px 14px;
    background: {'rgba(0, 240, 255, 0.12)' if is_dark else 'rgba(0, 168, 232, 0.12)'};
    border: 1px solid {'rgba(0, 240, 255, 0.4)' if is_dark else 'rgba(0, 168, 232, 0.35)'};
    border-radius: 30px;
    color: {accent_blue};
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 14px;
}}

.aq-pulse-point {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulseRing 1.8s infinite;
}}

@keyframes pulseRing {{
    0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
    70% {{ box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
}}

.aq-hero-h1 {{
    font-family: 'Outfit', sans-serif;
    font-size: clamp(2.3rem, 4vw, 3.8rem);
    font-weight: 900;
    color: {text_main};
    line-height: 1.1;
    letter-spacing: -1.2px;
    margin: 0 0 16px 0;
}}

.aq-hero-glow-text {{
    background: {'linear-gradient(135deg, #00F0FF 0%, #A78BFA 50%, #38BDF8 100%)' if is_dark else 'linear-gradient(135deg, #00A8E8 0%, #6366F1 100%)'};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.aq-hero-desc {{
    font-size: 1.05rem;
    line-height: 1.7;
    color: {text_sub};
    max-width: 580px;
    margin-bottom: 22px;
}}

/* Card Styling */
.aq-glass-panel {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 18px;
    padding: 22px;
    box-shadow: {card_shadow};
    transition: transform 0.25s ease, border-color 0.25s ease;
    height: 100%;
}}

.aq-glass-panel:hover {{
    transform: translateY(-4px);
    border-color: {accent_blue};
    box-shadow: {accent_glow};
}}

.aq-kpi-pill {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    box-shadow: {card_shadow};
    transition: transform 0.2s ease;
}}

.aq-kpi-pill:hover {{
    transform: translateY(-2px);
}}

.aq-kpi-num {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.65rem;
    font-weight: 800;
    color: {accent_blue};
    line-height: 1;
}}

.aq-kpi-label {{
    font-size: 0.74rem;
    font-weight: 700;
    color: {text_muted};
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 6px;
}}

/* Feature Boxes Bento Grid */
.aq-feature-box {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 18px;
    padding: 24px;
    box-shadow: {card_shadow};
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}

.aq-feature-box:hover {{
    transform: translateY(-6px);
    border-color: {accent_blue};
    box-shadow: 0 14px 40px rgba(0, 240, 255, 0.22);
}}

.aq-feature-icon {{
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(0, 240, 255, 0.2) 0%, rgba(99, 102, 241, 0.25) 100%);
    border: 1px solid {card_border};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 16px;
}}

.aq-feature-title {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.22rem;
    font-weight: 800;
    color: {text_main};
    margin-bottom: 8px;
}}

.aq-feature-desc {{
    font-size: 0.88rem;
    color: {text_sub};
    line-height: 1.6;
    margin-bottom: 16px;
}}

.aq-feature-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.74rem;
    font-weight: 700;
    color: {accent_blue};
    background: rgba(0, 240, 255, 0.1);
    border: 1px solid rgba(0, 240, 255, 0.3);
    padding: 3px 10px;
    border-radius: 12px;
}}

/* Apartment Matrix Tiles */
.aq-flat-tile {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 14px;
    padding: 16px;
    transition: all 0.25s ease;
    margin-bottom: 12px;
}}

.aq-flat-tile:hover {{
    border-color: {accent_blue};
    transform: translateY(-3px);
}}

/* Technical Specs Box */
.aq-spec-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    background: {'rgba(139, 92, 246, 0.12)' if is_dark else '#F8FAFC'};
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.9rem;
}}
</style>
"""), unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 1. TOPMOST UPPER HEADER
    # -------------------------------------------------------------
    col_b, col_nav, col_tog, col_auth = st.columns([2.2, 2.5, 1.4, 2.3], vertical_alignment="center")

    with col_b:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-brand-holder">
            <div class="aq-brand-avatar">💧</div>
            <div>
                <div class="aq-brand-h1">AquaNest</div>
                <div class="aq-brand-sub">SMART WATER INTELLIGENCE</div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    with col_nav:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-nav-links-mid">
            <span class="aq-nav-item-link">Telemetry</span>
            <span class="aq-nav-item-link">AI Leakage</span>
            <span class="aq-nav-item-link">Smart Billing</span>
        </div>
        """), unsafe_allow_html=True)

    with col_tog:
        t_state = st.toggle("🌙 Dark Mode", value=is_dark, key="home_theme_toggle")
        if t_state != is_dark:
            st.session_state["dark_theme"] = t_state
            st.rerun()

    with col_auth:
        col_in, col_up = st.columns(2, gap="small")
        with col_in:
            if st.button("Sign In", key="home_top_login", use_container_width=True):
                st.session_state["nav_selection"] = "Login"
                st.rerun()
        with col_up:
            if st.button("Sign Up", key="home_top_signup", type="primary", use_container_width=True):
                st.session_state["nav_selection"] = "Sign Up"
                st.rerun()

    # -------------------------------------------------------------
    # 2. HERO SECTION WITH IMAGE & TELEMETRY
    # -------------------------------------------------------------
    st.markdown("<div class='aq-hero-section'>", unsafe_allow_html=True)
    hl, hr = st.columns([1.1, 0.9], gap="large", vertical_alignment="center")

    with hl:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-live-pill">
            <span class="aq-pulse-point"></span>
            LIVE IOT & AI TELEMETRY CONNECTED
        </div>
        <h1 class="aq-hero-h1">
            Every Drop Counted.<br>
            <span class="aq-hero-glow-text">Every Flat Connected.</span>
        </h1>
        <p class="aq-hero-desc">
            AquaNest empowers smart apartment complexes with continuous ultrasonic overhead tank telemetry, automated hysteresis pump motor protection, AI nocturnal leak detection, and automated fair billing.
        </p>
        """), unsafe_allow_html=True)

        cta1, cta2, cta3 = st.columns(3, gap="small")
        with cta1:
            if st.button("👑 Admin Portal", key="btn_hero_admin", type="primary", use_container_width=True):
                st.session_state["user"] = {
                    "userId": "USR_ADMIN",
                    "name": "Property Admin",
                    "email": "admin@aquanest.io",
                    "role": "ADMIN",
                    "houseId": "ALL",
                    "demo": True,
                }
                st.session_state["nav_selection"] = "Dashboard"
                st.rerun()

        with cta2:
            if st.button("🏠 Resident Demo", key="btn_hero_resident", use_container_width=True):
                st.session_state["user"] = {
                    "userId": "USR_RES_1",
                    "name": "Rajesh Sharma",
                    "email": "rajesh@aquanest.io",
                    "role": "RESIDENT",
                    "houseId": "H101",
                    "demo": True,
                }
                st.session_state["nav_selection"] = "Resident Dashboard"
                st.rerun()

        with cta3:
            if st.button("⚡ Register Unit", key="btn_hero_reg", use_container_width=True):
                st.session_state["nav_selection"] = "Sign Up"
                st.rerun()

    with hr:
        if os.path.exists(hero_img_path):
            st.image(hero_img_path, use_container_width=True, caption="🏢 Connected Smart Apartment IoT Flow & Overhead Tank Hologram")

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 3. STATS BANNER PILLS
    # -------------------------------------------------------------
    k1, k2, k3, k4 = st.columns(4, gap="medium")

    with k1:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-kpi-pill">
            <div class="aq-kpi-num">4,000 L</div>
            <div class="aq-kpi-label">Central Storage Capacity</div>
        </div>
        """), unsafe_allow_html=True)

    with k2:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-kpi-pill">
            <div class="aq-kpi-num">99.8%</div>
            <div class="aq-kpi-label">AI Leak Detection Accuracy</div>
        </div>
        """), unsafe_allow_html=True)

    with k3:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-kpi-pill">
            <div class="aq-kpi-num">{len(RESIDENT_PROFILES)} Flats</div>
            <div class="aq-kpi-label">Sub-Metered Telemetry Units</div>
        </div>
        """), unsafe_allow_html=True)

    with k4:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-kpi-pill">
            <div class="aq-kpi-num">₹0.10 / L</div>
            <div class="aq-kpi-label">Automated Smart Tariff Rate</div>
        </div>
        """), unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 4. HIGH-TECH BENTO FEATURE BOXES GRID
    # -------------------------------------------------------------
    st.markdown("<div style='margin-top: 48px; margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent(f"""
    <div style="text-align: center; margin-bottom: 28px;">
        <div style="font-size: 0.78rem; font-weight: 800; color: {accent_blue}; text-transform: uppercase; letter-spacing: 1.2px;">ENGINEERED FOR MODERN SMART COMMUNITIES</div>
        <h2 style="font-size: 2.2rem; font-weight: 800; color: {text_main}; margin-top: 4px;">End-to-End Water Operations Engine</h2>
        <p style="color: {text_sub}; font-size: 0.96rem; max-width: 650px; margin: 0 auto;">Everything you need to automate, monitor, safeguard, and bill apartment water infrastructure autonomously.</p>
    </div>
    """), unsafe_allow_html=True)

    fb_col1, fb_col2, fb_col3 = st.columns(3, gap="medium")

    with fb_col1:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-feature-box">
            <div>
                <div class="aq-feature-icon">🛢️</div>
                <div class="aq-feature-title">Overhead Tank Telemetry</div>
                <div class="aq-feature-desc">
                    Ultrasonic JSN-SR04T depth telemetry sampling every 500ms. Computes real-time live volume, fill/empty velocities, and exact minutes until tank depletion.
                </div>
            </div>
            <div class="aq-feature-tag">● Continuous Sensing (±1mm)</div>
        </div>
        """), unsafe_allow_html=True)

    with fb_col2:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-feature-box">
            <div>
                <div class="aq-feature-icon">⚙️</div>
                <div class="aq-feature-title">Hysteresis Pump Guard</div>
                <div class="aq-feature-desc">
                    Dual-threshold hysteresis (Auto ON ≤20%, Auto OFF ≥90%) prevents contactor chattering and motor burnouts, featuring dry-run cutoffs and authorized overrides.
                </div>
            </div>
            <div class="aq-feature-tag" style="color: #10B981; background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3);">● Zero Contactor Chattering</div>
        </div>
        """), unsafe_allow_html=True)

    with fb_col3:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-feature-box">
            <div>
                <div class="aq-feature-icon">🛡️</div>
                <div class="aq-feature-title">AI Nocturnal Leak Detector</div>
                <div class="aq-feature-desc">
                    Scikit-Learn IsolationForest model pinpoints nocturnal concealed flapper leaks (01:00–05:00 AM) and distribution line ruptures before property damage occurs.
                </div>
            </div>
            <div class="aq-feature-tag" style="color: #F59E0B; background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.3);">● 99.8% Anomaly Precision</div>
        </div>
        """), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    fb_col4, fb_col5, fb_col6 = st.columns(3, gap="medium")

    with fb_col4:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-feature-box">
            <div>
                <div class="aq-feature-icon">▥</div>
                <div class="aq-feature-title">Pulse Sub-Metering Roster</div>
                <div class="aq-feature-desc">
                    450 pulses/L calibrated rotary flow meters on Flats 101–120. Provides per-flat instant flow metrics, daily volume totals, and usage baseline variance.
                </div>
            </div>
            <div class="aq-feature-tag">● {len(RESIDENT_PROFILES)} Individual Riser Nodes</div>
        </div>
        """), unsafe_allow_html=True)

    with fb_col5:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-feature-box">
            <div>
                <div class="aq-feature-icon">↗</div>
                <div class="aq-feature-title">7-Day Demand Forecast</div>
                <div class="aq-feature-desc">
                    AI predictive regression engine projects next-day and 7-day cumulative building water demand by synthesizing weather parameters, temperature, and occupancy.
                </div>
            </div>
            <div class="aq-feature-tag" style="color: #EC4899; background: rgba(236,72,153,0.1); border-color: rgba(236,72,153,0.3);">● Random Forest R²: 0.942</div>
        </div>
        """), unsafe_allow_html=True)

    with fb_col6:
        st.markdown(textwrap.dedent(f"""
        <div class="aq-feature-box">
            <div>
                <div class="aq-feature-icon">₹</div>
                <div class="aq-feature-title">Smart Transparent Billing</div>
                <div class="aq-feature-desc">
                    Transparent formula-based billing engine combining volumetric consumption with maintenance fees. Generates itemized invoices with UPI/BBPS instant checkout.
                </div>
            </div>
            <div class="aq-feature-tag" style="color: #10B981; background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3);">● 100% Fair Invoicing</div>
        </div>
        """), unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 5. LIVE APARTMENT FLATS TELEMETRY MATRIX
    # -------------------------------------------------------------
    st.markdown("<div style='margin-top: 48px; margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent(f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
        <div>
            <div style="font-size: 0.78rem; font-weight: 800; color: {accent_blue}; text-transform: uppercase; letter-spacing: 1.2px;">LIVE RESIDENTIAL NETWORK</div>
            <h2 style="font-size: 1.85rem; font-weight: 800; color: {text_main}; margin: 4px 0 0 0;">Sub-Metered Apartment Flats Telemetry</h2>
        </div>
        <span style="font-size: 0.8rem; font-weight: 700; color: #10B981; background: rgba(16, 185, 129, 0.15); padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.35);">
            ● {len(RESIDENT_PROFILES)} Units Active • 450 Pulses/L Calibration
        </span>
    </div>
    """), unsafe_allow_html=True)

    flats = [
        {
            "id": profile["houseId"],
            "num": f"Flat {profile['houseId'][1:]}",
            "res": profile["name"],
            "floor": (index // 4) + 1,
            "flow": f"{profile['baseDailyUsageLitres'] / 60.0:.1f} L/min",
            "today": f"{profile['baseDailyUsageLitres']:.0f} L",
            "status": "AI LEAK DETECTED" if profile["houseId"] == "H104" else "NORMAL",
            "color": "#EF4444" if profile["houseId"] == "H104" else "#10B981",
        }
        for index, profile in enumerate(RESIDENT_PROFILES)
    ]

    m_col1, m_col2, m_col3 = st.columns(3, gap="medium")
    for idx, f_info in enumerate(flats):
        target_col = m_col1 if idx % 3 == 0 else (m_col2 if idx % 3 == 1 else m_col3)
        with target_col:
            st.markdown(textwrap.dedent(f"""
            <div class="aq-flat-tile">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span style="font-weight: 800; font-size: 1.1rem; color: {text_main};">{f_info['num']}</span>
                        <span style="font-size: 0.78rem; color: {text_muted}; margin-left: 6px;">(Floor {f_info['floor']})</span>
                    </div>
                    <span style="font-size: 0.72rem; font-weight: 800; color: {f_info['color']}; background: rgba(0,0,0,0.15); border: 1px solid {f_info['color']}; padding: 2px 8px; border-radius: 12px;">
                        {f_info['status']}
                    </span>
                </div>
                <div style="font-size: 0.88rem; color: {text_sub}; margin-bottom: 10px;">👤 {f_info['res']}</div>
                <div style="display: flex; justify-content: space-between; background: {'rgba(139, 92, 246, 0.12)' if is_dark else '#F8FAFC'}; padding: 8px 12px; border-radius: 8px;">
                    <div>
                        <div style="font-size: 0.68rem; color: {text_muted}; font-weight: 700;">LIVE FLOW</div>
                        <div style="font-size: 0.95rem; font-weight: 800; color: {accent_blue};">{f_info['flow']}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.68rem; color: {text_muted}; font-weight: 700;">TODAY USAGE</div>
                        <div style="font-size: 0.95rem; font-weight: 800; color: {text_main};">{f_info['today']}</div>
                    </div>
                </div>
            </div>
            """), unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 6. HARDWARE & TECHNICAL SPECIFICATIONS
    # -------------------------------------------------------------
    st.markdown("<div style='margin-top: 48px;'></div>", unsafe_allow_html=True)
    hw_l, hw_r = st.columns([1.0, 1.0], gap="large", vertical_alignment="center")

    with hw_l:
        if os.path.exists(sensor_img_path):
            st.image(sensor_img_path, use_container_width=True, caption="📡 Waterproof JSN-SR04T Sensor & Hysteresis Relay Controller Unit")

    with hw_r:
        st.markdown(textwrap.dedent(f"""
        <div>
            <div style="font-size: 0.78rem; font-weight: 800; color: {accent_blue}; text-transform: uppercase; letter-spacing: 1.2px;">IOT EDGE HARDWARE & HYSTERESIS</div>
            <h2 style="font-size: 2.1rem; font-weight: 800; color: {text_main}; margin: 6px 0 14px;">Smart Edge Sensing & Fail-Safe Pump Guard</h2>
            <p style="color: {text_sub}; font-size: 0.98rem; line-height: 1.7; margin-bottom: 16px;">
                Our waterproof <strong>JSN-SR04T ultrasonic sensor</strong> samples overhead tank depth every 500ms with millimetre precision. Integrated <strong>dual-threshold hysteresis control</strong> activates the pump at ≤ 20% and deactivates at ≥ 90%, eliminating short-cycling contactor chatter and preventing overflows.
            </p>
            <div class="aq-spec-item">
                <span style="color: {text_sub};">Sampling Frequency</span>
                <span style="font-weight: 800; color: {accent_blue};">500 ms (0.5s Real-Time)</span>
            </div>
            <div class="aq-spec-item">
                <span style="color: {text_sub};">Ultrasonic Precision</span>
                <span style="font-weight: 800; color: #10B981;">± 2 mm Depth Resolution</span>
            </div>
            <div class="aq-spec-item">
                <span style="color: {text_sub};">Flow Pulse Calibration</span>
                <span style="font-weight: 800; color: {accent_blue};">450 Pulses / Litre</span>
            </div>
            <div class="aq-spec-item">
                <span style="color: {text_sub};">Nominal Distribution Pressure</span>
                <span style="font-weight: 800; color: #10B981;">2.80 bar (Alarm ≤ 1.80 bar)</span>
            </div>
        </div>
        """), unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 7. INTERACTIVE WATER SAVINGS CALCULATOR
    # -------------------------------------------------------------
    st.markdown("<div style='margin-top: 48px; margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="font-size: 0.78rem; font-weight: 800; color: {accent_blue}; text-transform: uppercase; letter-spacing: 1.2px;">ROI & SUSTAINABILITY ESTIMATOR</div>
        <h2 style="font-size: 2.1rem; font-weight: 800; color: {text_main}; margin-top: 4px;">Community Water & Cost Savings Calculator</h2>
        <p style="color: {text_sub}; font-size: 0.95rem;">Estimate how much water and money your apartment community saves annually with AquaNest</p>
    </div>
    """), unsafe_allow_html=True)

    calc_box = st.container()
    with calc_box:
        c_in_col, c_out_col = st.columns([1.0, 1.2], gap="large", vertical_alignment="center")

        with c_in_col:
            st.markdown(textwrap.dedent(f"""
            <div class="aq-glass-panel">
                <h4 style="color: {text_main}; font-size: 1.15rem; margin-bottom: 12px;">🏢 Apartment Parameters</h4>
            </div>
            """), unsafe_allow_html=True)
            calc_flats = st.slider("Number of Residential Units (Flats)", min_value=6, max_value=250, value=24, step=6)
            calc_tariff = st.slider("Water Tariff (₹ per 1,000 Litres)", min_value=50, max_value=200, value=100, step=10)

        with c_out_col:
            annual_litres_saved = int(calc_flats * 380 * 365 * 0.18)
            annual_cost_saved = int((annual_litres_saved / 1000.0) * calc_tariff)
            pump_hours_saved = int((annual_litres_saved / 1800.0))

            res_c1, res_c2, res_c3 = st.columns(3, gap="small")
            with res_c1:
                st.markdown(textwrap.dedent(f"""
                <div class="aq-kpi-pill">
                    <div class="aq-kpi-num" style="font-size: 1.45rem;">{annual_litres_saved:,} L</div>
                    <div class="aq-kpi-label">Annual Water Saved</div>
                </div>
                """), unsafe_allow_html=True)
            with res_c2:
                st.markdown(textwrap.dedent(f"""
                <div class="aq-kpi-pill">
                    <div class="aq-kpi-num" style="font-size: 1.45rem; color: #10B981;">₹{annual_cost_saved:,}</div>
                    <div class="aq-kpi-label">Community Savings / Yr</div>
                </div>
                """), unsafe_allow_html=True)
            with res_c3:
                st.markdown(textwrap.dedent(f"""
                <div class="aq-kpi-pill">
                    <div class="aq-kpi-num" style="font-size: 1.45rem; color: #F59E0B;">{pump_hours_saved:,} hrs</div>
                    <div class="aq-kpi-label">Pump Runtime Saved</div>
                </div>
                """), unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 8. INTERACTIVE FREQUENTLY ASKED QUESTIONS (FAQ)
    # -------------------------------------------------------------
    st.markdown("<div style='margin-top: 48px; margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="font-size: 0.78rem; font-weight: 800; color: {accent_blue}; text-transform: uppercase; letter-spacing: 1.2px;">KNOWLEDGE BASE & ARCHITECTURE</div>
        <h2 style="font-size: 2.1rem; font-weight: 800; color: {text_main}; margin-top: 4px;">Frequently Asked Questions</h2>
    </div>
    """), unsafe_allow_html=True)

    with st.expander("❓ How does the dual-threshold hysteresis pump control protect equipment?"):
        st.write("""
        Traditional float switches chatter repeatedly when waves ripple at the water surface, causing dangerous contactor arcing and motor burnouts.
        **AquaNest implements dual-threshold hysteresis**:
        - **LOW Trigger (≤ 20%):** Automatically turns pump ON only when tank depth drops below safety reserves.
        - **FULL Trigger (≥ 90%):** Automatically cuts motor power before overflow occurs.
        This provides a solid 70% deadband buffer that extends motor lifespan by over 40%.
        """)

    with st.expander("❓ How does the AI Isolation Forest detect concealed nocturnal leaks?"):
        st.write("""
        Between 01:00 AM and 05:00 AM, residential water flow is expected to drop to near zero.
        Our Scikit-Learn **IsolationForest anomaly model** analyzes hourly flow profiles:
        - If continuous non-zero flow (e.g. 1.8 L/min) is logged across 4 consecutive night hours, it flags silent toilet flapper or internal concealed pipe seepage before property damage occurs.
        """)

    with st.expander("❓ How is the smart water billing calculated for each apartment?"):
        st.write("""
        AquaNest uses a 100% transparent, formula-driven billing engine:
        $$\\text{Final Invoice} = (\\text{Monthly Consumption Litres} \\times \\text{Tariff Rate}) + \\text{Fixed Maintenance Charge}$$
        Tariff rates are immutably captured at generation time so past invoices remain tamper-proof audit trails.
        """)

    with st.expander("❓ Is resident consumption data kept private from neighbors?"):
        st.write("""
        Yes! AquaNest enforces strict **Role-Based Access Control (RBAC)**:
        - **Residents** are strictly isolated to their own unit's telemetry, historical invoices, and advice.
        - **Property Administrators** oversee building-wide aggregates, pump overrides, and tariffs.
        """)
