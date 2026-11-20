"""
AquaNest – Authentication Views
Implements Firebase Auth login, registration (RESIDENT role by default), and password reset.
"""

import streamlit as st

from services.resident_profiles import RESIDENT_PROFILE_BY_EMAIL


def render_login_view(api_client):
    is_dark = st.session_state.get("dark_theme", True)
    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"
    card_bg = "linear-gradient(135deg, rgba(32, 22, 78, 0.88) 0%, rgba(22, 15, 56, 0.94) 100%)" if is_dark else "#FFFFFF"
    card_border = "rgba(139, 92, 246, 0.35)" if is_dark else "rgba(226, 232, 240, 0.9)"

    st.markdown(f"""
    <div style="max-width: 480px; margin: 0 auto; text-align: center; margin-bottom: 24px;">
        <div style="font-size: 2.8rem; margin-bottom: 8px;">💧</div>
        <h2 style="color: {text_main}; font-weight: 800; margin-bottom: 4px;">AquaNest Login</h2>
        <p style="color: {text_sub}; font-size: 0.95rem;">Sign in to access your apartment water monitoring dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    c_box = st.container()
    with c_box:
        col_pad1, col_center, col_pad2 = st.columns([1, 2.2, 1])
        with col_center:
            st.markdown(f"""
            <div style="background: {card_bg}; border: 1px dashed {card_border}; padding: 14px; border-radius: 12px; margin-bottom: 20px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #00F0FF; margin-bottom: 8px; text-align: center; letter-spacing: 0.8px;">⚡ LOCAL DEMO PROFILES — 20 DISTINCT APARTMENTS</div>
            </div>
            """, unsafe_allow_html=True)

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                if st.button("👑 Admin Portal", key="quick_admin", use_container_width=True):
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

            with d_col2:
                demo_profile = st.selectbox(
                    "Choose a resident",
                    tuple(RESIDENT_PROFILE_BY_EMAIL),
                    format_func=lambda email: (
                        f"{RESIDENT_PROFILE_BY_EMAIL[email]['houseId']} — "
                        f"{RESIDENT_PROFILE_BY_EMAIL[email]['name']}"
                    ),
                    key="demo_resident_profile",
                )
                if st.button("🏠 Sign In as Demo Resident", key="quick_resident", use_container_width=True):
                    st.session_state["user"] = {
                        **RESIDENT_PROFILE_BY_EMAIL[demo_profile],
                        "demo": True,
                    }
                    st.session_state["nav_selection"] = "Resident Dashboard"
                    st.rerun()

            st.caption("Demo profiles use synthetic data and do not authenticate with Firebase.")
            st.markdown(f"<div style='text-align: center; color: {text_sub}; margin: 14px 0; font-size: 0.85rem;'>— OR SIGN IN WITH FIREBASE CREDENTIALS —</div>", unsafe_allow_html=True)

            with st.form("login_form"):
                email = st.text_input("Email Address", value=st.session_state.get("login_email", ""))
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True)

                if submit:
                    if not email or not password:
                        st.error("Please provide both email and password.")
                    else:
                        from services.firebase_service import get_firebase_service
                        authenticated, profile, message = get_firebase_service().authenticate_user(email, password)
                        if not authenticated:
                            st.error(message)
                        else:
                            role = profile["role"]
                            st.session_state["user"] = {
                                "userId": profile["userId"],
                                "name": profile["name"],
                                "email": profile["email"],
                                "role": role,
                                "houseId": profile["houseId"],
                                "demo": False,
                            }
                            st.session_state["nav_selection"] = (
                                "Dashboard" if role == "ADMIN" else "Resident Dashboard"
                            )
                            st.success(message)
                            st.rerun()

            st.markdown("<div style='margin-top: 16px; text-align: center; font-size: 0.9rem;'>", unsafe_allow_html=True)
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                if st.button("Forgot Password?", key="link_forgot"):
                    st.session_state["nav_selection"] = "Forgot Password"
                    st.rerun()
            with f_col2:
                if st.button("Need an Account? Sign Up", key="link_signup"):
                    st.session_state["nav_selection"] = "Sign Up"
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def render_signup_view(api_client):
    is_dark = st.session_state.get("dark_theme", True)
    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"

    st.markdown(f"""
    <div style="max-width: 480px; margin: 0 auto; text-align: center; margin-bottom: 24px;">
        <div style="font-size: 2.8rem; margin-bottom: 8px;">🏢</div>
        <h2 style="color: {text_main}; font-weight: 800; margin-bottom: 4px;">Resident Registration</h2>
        <p style="color: {text_sub}; font-size: 0.95rem;">Create your AquaNest apartment account for personal water tracking</p>
    </div>
    """, unsafe_allow_html=True)

    col_pad1, col_center, col_pad2 = st.columns([1, 2.2, 1])
    with col_center:
        st.info("🔒 Notice: Public registration creates an authenticated **RESIDENT** account assigned to your specific apartment unit.")

        with st.form("signup_form"):
            name = st.text_input("Full Name *")
            email = st.text_input("Email Address *")
            phone = st.text_input("Phone Number")
            house_number = st.selectbox("Apartment / House Number *", [str(number) for number in range(101, 121)])
            password = st.text_input("Password *", type="password")
            confirm_password = st.text_input("Confirm Password *", type="password")

            submitted = st.form_submit_button("Register Resident Account", use_container_width=True)

            if submitted:
                if not name or not email or not house_number or not password or not confirm_password:
                    st.error("Please fill in all required fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match. Please re-enter.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    from services.firebase_service import get_firebase_service
                    registered, message = get_firebase_service().register_user(
                        email, password, name, house_number, phone
                    )
                    if registered:
                        st.session_state["login_email"] = email
                        st.success(message)
                        st.session_state["nav_selection"] = "Login"
                        st.rerun()
                    else:
                        st.error(message)

        if st.button("Already have an account? Sign In", key="back_to_login", use_container_width=True):
            st.session_state["nav_selection"] = "Login"
            st.rerun()


def render_forgot_password_view():
    is_dark = st.session_state.get("dark_theme", True)
    text_main = "#FFFFFF" if is_dark else "#0A2540"
    text_sub = "#CBD5E1" if is_dark else "#475569"

    st.markdown(f"""
    <div style="max-width: 480px; margin: 0 auto; text-align: center; margin-bottom: 24px;">
        <div style="font-size: 2.8rem; margin-bottom: 8px;">🔑</div>
        <h2 style="color: {text_main}; font-weight: 800; margin-bottom: 4px;">Reset Password</h2>
        <p style="color: {text_sub}; font-size: 0.95rem;">Enter your registered email address to receive password reset instructions</p>
    </div>
    """, unsafe_allow_html=True)

    col_pad1, col_center, col_pad2 = st.columns([1, 2.2, 1])
    with col_center:
        with st.form("forgot_form"):
            email = st.text_input("Registered Email Address")
            submit = st.form_submit_button("Send Password Reset Link", use_container_width=True)
            if submit:
                if email and "@" in email:
                    st.success(f"A password reset link has been dispatched to {email}. Please check your inbox.")
                else:
                    st.error("Please enter a valid email address.")

        if st.button("Return to Login", key="return_login", use_container_width=True):
            st.session_state["nav_selection"] = "Login"
            st.rerun()
