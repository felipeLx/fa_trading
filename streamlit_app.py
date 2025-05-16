import streamlit as st
import pandas as pd
from database import fetch_historical_prices, fetch_balance_sheet_data, fetch_asset_analysis
from robot import monitor_and_trade
from technical_analysis import run_technical_analysis
import os
import pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]


def login():
    flow = Flow.from_client_config(
        {
            "installed": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["https://fatrading-7gfnxhrmeoknbjri7zanvg.streamlit.app/"],
            }
        },
        scopes=SCOPES,
        redirect_uri="https://fatrading-7gfnxhrmeoknbjri7zanvg.streamlit.app/"
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.session_state['flow'] = flow
    st.session_state['auth_url'] = auth_url
    st.session_state['login_requested'] = True

def logout():
    st.session_state.clear()

def main():
    st.title("InvestFal Dashboard")
    # Handle OAuth callback
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code = query_params["code"][0]
        flow = st.session_state.get('flow')
        if flow:
            flow.fetch_token(code=code)
            credentials = flow.credentials
            st.session_state['credentials'] = credentials
            st.session_state['login_requested'] = False

    # If logged in, show user info and logout
    if 'credentials' in st.session_state:
        credentials = st.session_state['credentials']
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        st.write("Logged in as:", user_info["email"])
        st.image(user_info["picture"])
        if st.button("Logout"):
            logout()
            st.experimental_rerun()
        # ... your dashboard code here ...
    else:
        # Not logged in
        if st.button("Login with Google"):
            login()
            st.experimental_rerun()
        if st.session_state.get('login_requested'):
            st.markdown(f"[Click here to authenticate]({st.session_state['auth_url']})")

    if 'credentials' in st.session_state:
        # Navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Asset Overview", "Best Asset to Trade", "Run Robot"])

        if page == "Asset Overview":
            st.header("Asset Overview")
            tickers = ["PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3", "ITSA4", "RDOR3", "RAIZ4", "PETZ3", "PSSA3", "VBBR3"]
            selected_ticker = st.selectbox("Select Ticker:", tickers, index=0)
            st.subheader(f"Data for {selected_ticker}")
            st.write("### Balance Sheet Data")
            balance_sheet_data = fetch_balance_sheet_data(selected_ticker)
            if not balance_sheet_data.empty:
                st.dataframe(balance_sheet_data)
            else:
                st.write("No balance sheet data available.")
            st.write("### Asset Analysis Data")
            asset_analysis_data = fetch_asset_analysis(selected_ticker)
            if not asset_analysis_data.empty:
                st.dataframe(asset_analysis_data)
            else:
                st.write("No asset analysis data available.")
            st.write("### Historical Prices and Indicators")
            historical_prices = fetch_historical_prices(selected_ticker)
            if not historical_prices.empty:
                st.dataframe(historical_prices)
                st.line_chart(historical_prices.set_index("date")["close"])
            else:
                st.write("No historical price data available.")

        elif page == "Best Asset to Trade":
            st.header("Find the Best Asset to Trade")
            if st.button("Run Technical Analysis"):
                st.write("Running technical analysis to find the best asset...")
                run_technical_analysis()
                st.success("Technical analysis completed. Check the database for results.")

        elif page == "Run Robot":
            st.header("Run Trading Robot")
            if st.button("Start Trading Robot"):
                st.write("Starting the trading robot...")
                account_balance = 10000  # Example account balance in R$
                risk_per_trade = 0.02  # Risk 2% of account balance per trade
                monitor_and_trade(account_balance, risk_per_trade)
                st.success("Trading robot is running.")

if __name__ == "__main__":
    main()