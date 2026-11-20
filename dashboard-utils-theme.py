"""
AquaNest Design System & Visual Styling
Provides full-viewport Light and Deep Navy-Purplish Dark Mode styling,
removes default top padding so the custom header is at the top edge, and exports all chart tokens.
"""

import streamlit as st
import plotly.graph_objects as go

# Color Tokens
PRIMARY_AQUA = "#00A8E8"
CYAN_ACCENT = "#00F0FF"
DEEP_NAVY = "#0A2540"
NAVY_SURFACE = "#0D3B66"
NAVY_PURPLE = "#160F38"
SUCCESS_TEAL = "#10B981"
WARNING_AMBER = "#F59E0B"
DANGER_CORAL = "#EF4444"
BG_LIGHT = "#F8FAFC"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#0F172A"
TEXT_MUTED = "#64748B"
BORDER_COLOR = "#E2E8F0"


def inject_custom_css():
    if "dark_theme" not in st.session_state:
        st.session_state["dark_theme"] = True

    is_dark = st.session_state["dark_theme"]

    if is_dark:
        bg_full = "linear-gradient(135deg, #0D0827 0%, #160F38 35%, #1D134E 70%, #0F092B 100%)"
        bg_solid = "#120B30"
        card_bg_css = "linear-gradient(135deg, rgba(32, 22, 78, 0.88) 0%, rgba(22, 15, 56, 0.94) 100%)"
        card_border_css = "rgba(139, 92, 246, 0.4)"
        text_pri_css = "#FFFFFF"
        text_sec_css = "#CBD5E1"
        text_mut_css = "#A5B4FC"
        metric_bg_css = "rgba(28, 19, 70, 0.9)"
        metric_val_css = "#00F0FF"
        input_bg_css = "rgba(28, 19, 70, 0.95)"
        sidebar_bg_css = "linear-gradient(180deg, #0D0827 0%, #08051A 100%)"
        glow_shadow_css = "0 8px 30px rgba(0, 240, 255, 0.25)"
    else:
        bg_full = "linear-gradient(180deg, #F0F6FF 0%, #FFFFFF 50%, #F8FAFC 100%)"
        bg_solid = "#F8FAFC"
        card_bg_css = "#FFFFFF"
        card_border_css = "#E2E8F0"
        text_pri_css = "#0A2540"
        text_sec_css = "#334155"
        text_mut_css = "#64748B"
        metric_bg_css = "#FFFFFF"
        metric_val_css = "#0A2540"
        input_bg_css = "#FFFFFF"
        sidebar_bg_css = "linear-gradient(180deg, #0A2540 0%, #061B2E 100%)"
        glow_shadow_css = "0 8px 24px rgba(10, 37, 64, 0.08)"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* 1. Remove Streamlit top header blank space while keeping sidebar toggle button accessible */
        header[data-testid="stHeader"] {{
            background: transparent !important;
            height: 2.5rem !important;
            z-index: 100 !important;
        }}

        [data-testid="stSidebarCollapseButton"],
        button[data-testid="stSidebarCollapseButton"] {{
            color: #00F0FF !important;
            background: rgba(30, 19, 74, 0.85) !important;
            border: 1px solid rgba(139, 92, 246, 0.45) !important;
            border-radius: 8px !important;
            visibility: visible !important;
        }}

        .main .block-container {{
            padding-top: 1.0rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 100% !important;
        }}

        /* 2. Full Viewport Background */
        html, body, .stApp, [data-testid="stAppViewContainer"], section.main, .main {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background: {bg_full} !important;
            background-color: {bg_solid} !important;
            color: {text_pri_css} !important;
            transition: background 0.35s ease, color 0.35s ease !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Outfit', sans-serif !important;
            color: {text_pri_css} !important;
            letter-spacing: -0.4px;
        }}

        p, span, div, label {{
            color: {text_pri_css};
        }}

        /* 3. Metric Containers */
        div[data-testid="metric-container"] {{
            background: {metric_bg_css} !important;
            border: 1px solid {card_border_css} !important;
            padding: 16px 20px !important;
            border-radius: 16px !important;
            box-shadow: {glow_shadow_css} !important;
            transition: transform 0.22s ease, border-color 0.22s ease !important;
        }}

        div[data-testid="metric-container"]:hover {{
            transform: translateY(-3px) !important;
            border-color: #00F0FF !important;
        }}

        div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: {metric_val_css} !important;
        }}

        div[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
            color: {text_mut_css} !important;
            font-weight: 700 !important;
        }}

        /* 4. Form inputs & Selectors */
        div[data-testid="stTextInput"] input, 
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div,
        div[data-testid="stMultiSelect"] > div {{
            background: {input_bg_css} !important;
            color: {text_pri_css} !important;
            border: 1px solid {card_border_css} !important;
            border-radius: 8px !important;
        }}

        /* 5. Sidebar */
        section[data-testid="stSidebar"],
        [data-testid="stSidebar"] {{
            background: {sidebar_bg_css} !important;
            color: #FFFFFF !important;
            border-right: 1px solid rgba(139, 92, 246, 0.35) !important;
        }}
        [data-testid="stSidebar"] * {{
            color: #E2E8F0 !important;
        }}
        [data-testid="stSidebarCollapseButton"],
        button[data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebarCollapsedControl"] {{
            color: #00F0FF !important;
            background: rgba(30, 19, 74, 0.95) !important;
            border: 1px solid rgba(139, 92, 246, 0.5) !important;
            border-radius: 8px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            visibility: visible !important;
        }}

        /* 6. Universal Button Styling - Eliminates ANY white button backgrounds */
        button,
        .stButton > button,
        button[data-testid="stBaseButton-secondary"],
        button[data-testid="stBaseButton-primary"],
        button[kind="secondary"],
        button[kind="primary"] {{
            background: linear-gradient(135deg, rgba(35, 23, 85, 0.95) 0%, rgba(24, 15, 62, 0.95) 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(139, 92, 246, 0.45) !important;
            border-radius: 10px !important;
            padding: 8px 20px !important;
            font-weight: 700 !important;
            font-size: 0.92rem !important;
            transition: all 0.25s ease !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
        }}

        button:hover,
        .stButton > button:hover,
        button[data-testid="stBaseButton-secondary"]:hover {{
            background: linear-gradient(135deg, rgba(55, 36, 125, 0.95) 0%, rgba(38, 24, 98, 0.95) 100%) !important;
            border-color: #00F0FF !important;
            color: #00F0FF !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0, 240, 255, 0.35) !important;
        }}

        button[data-testid="stBaseButton-primary"],
        button[kind="primary"],
        .stButton > button[kind="primary"],
        .stButton > button[type="primary"] {{
            background: linear-gradient(135deg, #00A8E8 0%, #6366F1 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 16px rgba(0, 168, 232, 0.4) !important;
        }}

        button[data-testid="stBaseButton-primary"]:hover,
        button[kind="primary"]:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 24px rgba(0, 240, 255, 0.6) !important;
        }}

        /* 7. Eliminate ALL white codeblocks, pre tags, and markdown artifacts */
        pre, code, kbd, samp {{
            background: rgba(22, 15, 56, 0.95) !important;
            color: #00F0FF !important;
            border: 1px solid rgba(139, 92, 246, 0.3) !important;
            border-radius: 8px !important;
        }}

        /* 8. Alert / Toast / Notification Containers */
        div[data-testid="stAlert"],
        div[data-testid="stNotification"],
        div[data-testid="stToast"] {{
            background: rgba(22, 15, 56, 0.95) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(139, 92, 246, 0.4) !important;
            border-radius: 12px !important;
        }}

        /* 9. Dataframe and Table Containers */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {{
            background: rgba(22, 15, 56, 0.8) !important;
            border: 1px solid rgba(139, 92, 246, 0.3) !important;
            border-radius: 12px !important;
        }}

        /* 10. Expander Containers */
        div[data-testid="stExpander"] {{
            background: rgba(26, 17, 68, 0.75) !important;
            border: 1px solid rgba(139, 92, 246, 0.35) !important;
            border-radius: 12px !important;
        }}

        /* 11. Tabs */
        div[data-testid="stTabs"] button[role="tab"] {{
            color: #CBD5E1 !important;
            background: transparent !important;
        }}
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
            color: #00F0FF !important;
            border-bottom: 2px solid #00F0FF !important;
        }}

        /* 11b. Modal Dialogs & Chatbot Popup */
        div[data-testid="stDialog"],
        div[role="dialog"],
        div[data-testid="stModal"] > div {{
            background: linear-gradient(135deg, #160F38 0%, #0D0827 100%) !important;
            background-color: #120B30 !important;
            border: 1px solid rgba(0, 240, 255, 0.45) !important;
            border-radius: 16px !important;
            box-shadow: 0 16px 50px rgba(0, 0, 0, 0.75) !important;
            color: #FFFFFF !important;
        }}

        div[data-testid="stDialog"] h2,
        div[role="dialog"] h2,
        div[data-testid="stDialog"] h3,
        div[role="dialog"] h3 {{
            color: #00F0FF !important;
        }}

        div[data-testid="stChatMessage"] {{
            background: rgba(26, 17, 68, 0.85) !important;
            border: 1px solid rgba(139, 92, 246, 0.3) !important;
            border-radius: 12px !important;
            margin-bottom: 8px !important;
            color: #FFFFFF !important;
        }}

        /* 12. AquaNest System Cards & Badges */
        .aq-card {{
            background: {card_bg_css} !important;
            border: 1px solid {card_border_css} !important;
            border-radius: 14px !important;
            box-shadow: {glow_shadow_css} !important;
        }}

        .aq-app-header {{
            background: linear-gradient(135deg, rgba(30, 19, 74, 0.95) 0%, rgba(13, 8, 39, 0.95) 100%) !important;
            border: 1px solid {card_border_css} !important;
            border-radius: 16px !important;
            padding: 22px 26px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35) !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            flex-wrap: wrap !important;
            gap: 14px !important;
        }}

        .aq-section-title {{
            background: linear-gradient(135deg, rgba(26, 16, 68, 0.95) 0%, rgba(18, 12, 48, 0.95) 100%) !important;
            border: 1px solid {card_border_css} !important;
            border-radius: 12px !important;
            padding: 14px 20px !important;
            margin-bottom: 16px !important;
            color: #FFFFFF !important;
        }}

        .aq-status-strip {{
            background: rgba(22, 15, 56, 0.85) !important;
            border: 1px solid {card_border_css} !important;
            border-radius: 12px !important;
            color: {text_sec_css} !important;
        }}

        .badge-live {{
            background: rgba(16, 185, 129, 0.15) !important;
            border: 1px solid rgba(16, 185, 129, 0.4) !important;
            color: #10B981 !important;
            border-radius: 20px !important;
            padding: 4px 12px !important;
            font-size: 12px !important;
            font-weight: 700 !important;
        }}

        .badge-critical {{
            background: rgba(239, 68, 68, 0.15) !important;
            border: 1px solid rgba(239, 68, 68, 0.4) !important;
            color: #EF4444 !important;
            border-radius: 20px !important;
            padding: 4px 12px !important;
            font-size: 12px !important;
            font-weight: 700 !important;
        }}

        .badge-demo {{
            background: rgba(245, 158, 11, 0.15) !important;
            border: 1px solid rgba(245, 158, 11, 0.4) !important;
            color: #F59E0B !important;
            border-radius: 20px !important;
            padding: 4px 12px !important;
            font-size: 12px !important;
            font-weight: 700 !important;
        }}

        .pulse-dot {{
            display: inline-block !important;
            width: 8px !important;
            height: 8px !important;
            border-radius: 50% !important;
            background: #10B981 !important;
            box-shadow: 0 0 8px #10B981 !important;
            margin-right: 6px !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def format_plotly_chart(fig, title="", height=360):
    is_dark = st.session_state.get("dark_theme", False)
    text_color = "#FFFFFF" if is_dark else "#0A2540"
    grid_color = "rgba(139, 92, 246, 0.2)" if is_dark else "#F1F5F9"

    fig.update_layout(
        title={
            'text': f"<b>{title}</b>" if title else "",
            'font': {'size': 14, 'color': text_color, 'family': 'Outfit, Plus Jakarta Sans'}
        },
        height=height,
        margin=dict(l=30, r=30, t=50 if title else 20, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans", size=12, color=text_color),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=text_color)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            linecolor=grid_color,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            linecolor=grid_color,
            zeroline=False
        )
    )
    return fig


def create_html_csv_download_button(df, filename, label=None, is_primary=True):
    """Generates an HTML5 <a> tag with explicit download attribute to force exact filename and .csv extension in Chrome."""
    import base64
    if label is None:
        label = f"📥 Download {filename}"
    csv_str = df.to_csv(index=False)
    csv_bytes = ('\ufeff' + csv_str).encode('utf-8')
    b64 = base64.b64encode(csv_bytes).decode('utf-8')
    bg_style = "linear-gradient(135deg, #00A8E8 0%, #6366F1 100%)" if is_primary else "linear-gradient(135deg, rgba(35, 23, 85, 0.95) 0%, rgba(24, 15, 62, 0.95) 100%)"
    border_style = "1px solid rgba(0, 240, 255, 0.6)" if is_primary else "1px solid rgba(139, 92, 246, 0.5)"
    text_color = "#FFFFFF" if is_primary else "#00F0FF"
    shadow_style = "0 6px 20px rgba(0, 168, 232, 0.45)" if is_primary else "0 4px 15px rgba(0, 0, 0, 0.3)"

    return f"""
    <a href="data:text/csv;charset=utf-8;base64,{b64}" download="{filename}"
       style="display: flex; align-items: center; justify-content: center; width: 100%;
              background: {bg_style}; border: {border_style}; color: {text_color} !important;
              text-decoration: none !important; font-weight: 800; font-size: 14px;
              border-radius: 12px; padding: 12px 20px; box-sizing: border-box;
              box-shadow: {shadow_style}; cursor: pointer; text-align: center;
              transition: all 0.2s ease-in-out; margin: 4px 0;">
        {label}
    </a>
    """

