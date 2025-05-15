import streamlit as st
import pandas as pd
from database import fetch_historical_prices, fetch_balance_sheet_data, fetch_daily_analysis, fetch_asset_analysis
from robot import monitor_and_trade

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
            page = st.sidebar.radio("Go to", ["Balance Sheet Data", "Historical Prices", "Best Asset to Trade"])

            if page == "Balance Sheet Data":
                st.header("Balance Sheet Data")
                ticker = st.text_input("Enter Ticker:")
                if ticker:
                    df = fetch_balance_sheet_data(ticker)
                    st.dataframe(df)

            elif page == "Historical Prices":
                st.header("Historical Prices")
                ticker = st.text_input("Enter Ticker:")
                if ticker:
                    df = fetch_historical_prices(ticker)
                    st.dataframe(df)

            elif page == "Best Asset to Trade":
                st.header("Best Asset to Trade")
                st.write("Running the trading robot to determine the best asset...")

                account_balance = 10000  # Example account balance in R$
                risk_per_trade = 0.02  # Risk 2% of account balance per trade

                # Call monitor_and_trade and capture the best asset
                best_asset = monitor_and_trade(account_balance, risk_per_trade)
                if best_asset:
                    st.success(f"The best asset to trade is: {best_asset}")
                else:
                    st.error("No suitable asset found for trading.")
        else:
            st.sidebar.error("Invalid username or password")

if __name__ == "__main__":
    main()
