import streamlit as st
import streamlit.components.v1 as components
import requests
import os
from dotenv import load_dotenv

load_dotenv()


# API_BASE = os.getenv("API_BASE", "http://web:8000")  # <-- web instead of 127.0.0.1

API_BASE = os.getenv("API_BASE", "http://web:8000")
PUBLIC_API_BASE = os.getenv("PUBLIC_API_BASE", "http://127.0.0.1:8000")

LOGIN_URL = f"{API_BASE}/api/auth/login"
REGISTER_URL = f"{API_BASE}/api/auth/register"
ME_URL = f"{API_BASE}/api/auth/me"



# API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
# LOGIN_URL = f"{API_BASE}/api/auth/login"
# REGISTER_URL = f"{API_BASE}/api/auth/register"
# ME_URL = f"{API_BASE}/api/auth/me"

st.set_page_config(page_title="Playlist App", layout="wide")

# -----------------------
# session state
# -----------------------
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

# -----------------------
# helpers
# -----------------------
def post_no_auth(path, payload):
    try:
        r = requests.post(API_BASE + path, json=payload, timeout=5)
        return r
    except Exception as e:
        return None

def post_with_auth(path, payload):
    try:
        headers = {"Authorization": f"Token {st.session_state.token}"} if st.session_state.token else {}
        r = requests.post(API_BASE + path, json=payload, headers=headers, timeout=5)
        return r
    except Exception:
        return None

# -----------------------
# LOGIN / REGISTER screen
# -----------------------
if not st.session_state.token:
    st.title("🔐 Login to Collaborative Playlist")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            r = post_no_auth("/api/auth/login", {"username": login_user, "password": login_pass})
            if r is None:
                st.error("Server unreachable")
            elif r.status_code == 200:
                data = r.json()
                st.session_state.token = data.get("token")
                st.session_state.username = data.get("username")
                st.success("Logged in")
                st.experimental_rerun()
            else:
                try:
                    st.error(r.json().get("error", "Login failed"))
                except Exception:
                    st.error("Login failed")

    with tab_register:
        reg_user = st.text_input("New username", key="reg_user")
        reg_pass = st.text_input("New password", type="password", key="reg_pass")
        if st.button("Register"):
            r = post_no_auth("/api/auth/register", {"username": reg_user, "password": reg_pass})
            if r is None:
                st.error("Server unreachable")
            elif r.status_code == 200:
                data = r.json()
                st.success("Account created — logging in")
                st.session_state.token = data.get("token")
                st.session_state.username = data.get("username")
                st.experimental_rerun()
            else:
                try:
                    st.error(r.json().get("error", "Registration failed"))
                except Exception:
                    st.error("Registration failed")
    st.stop()

# -----------------------
# Main app (after login)
# -----------------------
st.sidebar.success(f"Logged in as {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.token = None
    st.session_state.username = None
    st.experimental_rerun()

st.title("🎵 Collaborative Playlist ")








# Load HTML file
html_path = os.path.join("html_files", "ui.html")
if not os.path.exists(html_path):
    st.error(f"Missing {html_path}. Create it with the UI HTML provided.")
else:
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Inject API base, token and username
    # html_content = html_content.replace("__API__", API_BASE)

    html_content = html_content.replace("__API__", PUBLIC_API_BASE)


    token_value = st.session_state.token or ""
    username_value = st.session_state.username or ""

    html_content = html_content.replace("__TOKEN__", token_value)
    html_content = html_content.replace("__USER__", username_value)



    # # token might be None
    # token_value = st.session_state.token or ""
    # username_value = st.session_state.username or ""
    # # Escape quotes just in case
    # html_content = html_content.replace("__TOKEN__", token_value)
    # html_content = html_content.replace("__USER__", username_value)

    components.html(html_content, height=900, scrolling=True)
