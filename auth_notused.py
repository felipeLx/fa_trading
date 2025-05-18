import streamlit as st
import pandas as pd
from utils.database import fetch_historical_prices, fetch_balance_sheet_data, fetch_asset_analysis
#from utils.robot import monitor_and_trade
#from utils.technical_analysis import run_technical_analysis
import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = "https://fatrading-7gfnxhrmeoknbjri7zanvg.streamlit.app/oauth2callback"
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]


def login():
    flow = Flow.from_client_config(
        {
            "installed": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI, "http://localhost"],
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.session_state['flow'] = flow
    st.session_state['auth_url'] = auth_url
    st.session_state['login_requested'] = True

def logout():
    st.session_state.clear()

def main():
    st.title("InvestFal Dashboard")
    query_params = st.query_params
    # 1. Handle OAuth callback
    if "code" in query_params and 'credentials' not in st.session_state:
        code = query_params["code"][0] if isinstance(query_params["code"], list) else query_params["code"]
        flow = st.session_state.get('flow')
        if flow:
            flow.fetch_token(code=code)
            credentials = flow.credentials
            st.session_state['credentials'] = credentials
            st.session_state['login_requested'] = False
            st.experimental_set_query_params()  # Clean up URL after login
            st.rerun()  # Rerun to show dashboard
        else:
            st.error("OAuth flow not found. Please try again.")
            return

    # 2. If logged in, show dashboard
    if 'credentials' in st.session_state:
        credentials = st.session_state['credentials']
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        st.write("Logged in as:", user_info["email"])
        st.image(user_info["picture"])
        if st.button("Logout"):
            logout()
            st.rerun()
        # ... your dashboard code here ...
    else:
        # 3. Not logged in and not in callback: show only the Authenticate with Google button
        if 'flow' not in st.session_state or 'auth_url' not in st.session_state:
            login()
        st.markdown(
            f'<a href="{st.session_state["auth_url"]}" style="display:inline-block; padding:0.5em 1em; background:#4285F4; color:white; border-radius:4px; text-decoration:none; font-weight:bold;">Authenticate with Google</a>',
            unsafe_allow_html=True
        )

    if 'credentials' in st.session_state:
        return