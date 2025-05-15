import streamlit as st
import pandas as pd
from database import fetch_historical_prices, fetch_balance_sheet_data, fetch_daily_analysis, fetch_asset_analysis
from robot import monitor_and_trade
from technical_analysis import run_technical_analysis

def authenticate_user(username, password):
    """Simple authentication function."""
    # Replace this with a more secure authentication mechanism
    valid_users = {
        "admin": "password123",
        "user": "userpass"
    }
    return valid_users.get(username) == password

def main():
    st.title("InvestFal Dashboard")

    # Login Section
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if authenticate_user(username, password):
            st.sidebar.success("Login successful!")

            # Navigation
            st.sidebar.title("Navigation")
            page = st.sidebar.radio("Go to", ["Asset Overview", "Best Asset to Trade", "Run Robot"])

            if page == "Asset Overview":
                st.header("Asset Overview")

                # Select ticker
                tickers = ["PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3", "ITSA4", "RDOR3", "RAIZ4", "PETZ3", "PSSA3", "VBBR3"]
                selected_ticker = st.selectbox("Select Ticker:", tickers, index=0)

                # Fetch and display data
                st.subheader(f"Data for {selected_ticker}")

                # Balance Sheet Data
                st.write("### Balance Sheet Data")
                balance_sheet_data = fetch_balance_sheet_data(selected_ticker)
                if not balance_sheet_data.empty:
                    st.dataframe(balance_sheet_data)
                else:
                    st.write("No balance sheet data available.")

                # Asset Analysis Data
                st.write("### Asset Analysis Data")
                asset_analysis_data = fetch_asset_analysis(selected_ticker)
                if not asset_analysis_data.empty:
                    st.dataframe(asset_analysis_data)
                else:
                    st.write("No asset analysis data available.")

                # Historical Prices and Indicators
                st.write("### Historical Prices and Indicators")
                historical_prices = fetch_historical_prices(selected_ticker)
                if not historical_prices.empty:
                    st.dataframe(historical_prices)

                    # Example: Plot close prices
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
        else:
            st.sidebar.error("Invalid username or password")

if __name__ == "__main__":
    main()
