import streamlit as st
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib import get_user_credentials
import os
from dotenv import load_dotenv

load_dotenv()

if "user" not in st.session_state:
    st.session_state.user = None
if "credentials" not in st.session_state:
    st.session_state.credentials = None


def login_callback():
    credentials = get_user_credentials(
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/calendar.events.readonly",
        ],
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
    )
    id_info = id_token.verify_token(
        credentials.id_token,
        requests.Request(),
    )
    st.session_state.credentials = credentials
    st.session_state.user = id_info


if not st.session_state.user:
    st.button(
        "🔑 Login with Google",
        type="primary",
        on_click=login_callback,
    )
    st.stop()

if st.sidebar.button("Logout", type="primary"):
    st.session_state["user"] = None
    st.session_state["credentials"] = None
    st.rerun()

st.header(f"Hello {st.session_state.user['given_name']}")
st.image(st.session_state.user["picture"])

with st.sidebar:
    st.subheader("User info")
    st.json(st.session_state.user)

st.divider()
