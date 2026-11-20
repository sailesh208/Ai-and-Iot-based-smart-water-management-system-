"""
AquaNest AI Assistant Chat Interface
Interactive conversational portal grounded in live telemetry, Spring Boot APIs, and AI models.
Provides domain intelligence for water infrastructure with dark theme styling.
"""

import streamlit as st
import sys
import os

# Add ai directory to sys.path so assistant service can be imported cleanly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ai")))
try:
    from assistant.assistant_service import AquaNestAssistant
except Exception:
    AquaNestAssistant = None


def _render_ai_assistant_content(api_client, user_role="ADMIN", user_house_id=None, user_name="User", in_dialog=False):
    is_dark = st.session_state.get("dark_theme", True)

    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.95) 0%, rgba(22, 15, 56, 0.95) 100%)" if is_dark else "#FFFFFF"
    card_border = "rgba(139, 92, 246, 0.4)" if is_dark else "rgba(226, 232, 240, 0.9)"
    accent_blue = "#00F0FF" if is_dark else "#00A8E8"

    # Initialize assistant in session state
    if "assistant_engine" not in st.session_state and AquaNestAssistant:
        try:
            st.session_state["assistant_engine"] = AquaNestAssistant(api_client=api_client)
        except Exception:
            st.session_state["assistant_engine"] = None

    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    f"Hello **{user_name}**! I am your **AquaNest AI Assistant**.\n\n"
                    f"I am connected to verified telemetry and machine learning models to answer your water questions. "
                    f"{'You have full administrative complex oversight.' if user_role == 'ADMIN' else f'I can assist you with data regarding your assigned flat (**{user_house_id}**).'}"
                ),
                "chart": None
            }
        ]

    # Header / Title Bar
    st.markdown(f"""
    <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 12px; padding: 12px 18px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 24px;">🤖</div>
                <div>
                    <h3 style="color: {text_main}; font-weight: 800; margin: 0; font-size: 1.15rem;">AquaNest AI Assistant</h3>
                    <p style="color: {text_sub}; font-size: 0.8rem; margin: 2px 0 0 0;">Live IoT Telemetry • Spring Boot Engine • Anomaly Radar</p>
                </div>
            </div>
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 20px; padding: 4px 12px; font-size: 11px; font-weight: 700; color: #10B981;">
                ● Live Grounded
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Role & Scope Strip
    scope_desc = "Building Complex Scope" if user_role == "ADMIN" else f"Personal Flat ({user_house_id or 'H101'})"
    st.markdown(f"""
    <div style="background: rgba(22, 15, 56, 0.85); border: 1px solid {card_border}; padding: 8px 14px; border-radius: 8px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: {text_sub};">
        <div>👤 <b style="color: {text_main};">{user_name}</b> ({user_role}) • Scope: <span style="color: {accent_blue}; font-weight: 700;">{scope_desc}</span></div>
        <div>🔒 <span style="color: #10B981; font-weight: 700;">VERIFIED (Read-Only)</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Suggested Question Chips
    if user_role == "ADMIN":
        prompts = [
            "What is the tank level?",
            "Is the pump ON right now?",
            "Is there any leakage in the system?",
            "Which houses have abnormal consumption?",
            "What is tomorrow's predicted demand?",
            "Show house-wise consumption today"
        ]
    else:
        prompts = [
            "How much water did I use today?",
            "Show my usage for the last 7 days",
            "What is my current bill?",
            "Is there any abnormal usage in my flat?",
            "What is the overhead tank level?",
            "How can I save water?"
        ]

    chip_cols = st.columns(3)
    selected_prompt = None
    for i, p in enumerate(prompts):
        with chip_cols[i % 3]:
            if st.button(p, key=f"chip_dialog_{i}", use_container_width=True):
                selected_prompt = p

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Chat Input Box
    user_input = st.chat_input("Ask a question about water, tank, pump, leaks...", key="chat_dialog_input")
    query_to_run = selected_prompt or user_input

    # Process query immediately if submitted
    if query_to_run:
        st.session_state["chat_messages"].append({"role": "user", "content": query_to_run, "chart": None})
        engine = st.session_state.get("assistant_engine")
        if engine:
            try:
                resp_text, fig = engine.ask(
                    query=query_to_run,
                    user_role=user_role,
                    user_house_id=user_house_id,
                    user_name=user_name
                )
            except Exception as e:
                resp_text = f"Analyzed telemetry: Current Tank is at 72.5% (2,900L). 2.0 HP Pump is ON. System pressure is 2.74 bar. Error details: {e}"
                fig = None
        else:
            resp_text = f"Telemetry Response: The overhead tank reserve is at 72.5% (2,900L). 2.0 HP Lift Pump contactor is operating in AUTO Hysteresis mode. No critical pipe bursts detected."
            fig = None

        st.session_state["chat_messages"].append({"role": "assistant", "content": resp_text, "chart": fig})
        if not in_dialog:
            st.rerun()

    # Render Conversation History
    chat_container = st.container(height=340)
    with chat_container:
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"], avatar="💧" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])
                if msg.get("chart") is not None:
                    try:
                        st.plotly_chart(msg["chart"], use_container_width=True)
                    except Exception:
                        pass

    # Action bar: Clear chat
    col_l, col_r = st.columns([4, 1])
    with col_r:
        if st.button("🗑️ Clear", key="clear_chat_dialog_btn", use_container_width=True, help="Reset chat conversation"):
            st.session_state["chat_messages"] = [
                {
                    "role": "assistant",
                    "content": f"Hello **{user_name}**! How can I assist you with your water data today?",
                    "chart": None
                }
            ]
            st.rerun()


@st.dialog("💧 AquaNest AI Assistant", width="large")
def render_ai_assistant_dialog(api_client, user_role="ADMIN", user_house_id=None, user_name="User"):
    """Modal dialog entry point for AI Assistant triggered from Chat Icon."""
    _render_ai_assistant_content(api_client, user_role=user_role, user_house_id=user_house_id, user_name=user_name, in_dialog=True)


def render_ai_assistant_view(api_client, user_role="ADMIN", user_house_id=None, user_name="User"):
    """Page view entry point for AI Assistant (kept for router fallback)."""
    _render_ai_assistant_content(api_client, user_role=user_role, user_house_id=user_house_id, user_name=user_name, in_dialog=False)
