import streamlit as st
import pandas as pd
from database import fetch_historical_prices, fetch_balance_sheet_data, fetch_asset_analysis
from robot import monitor_and_trade
from technical_analysis import run_technical_analysis

# --- Google Auth via Streamlit Cloud ---

def main():
    st.title("InvestFal Dashboard")

    # Use Streamlit's built-in Google authentication
    if not hasattr(st, "user") or not st.user.is_logged_in:
        st.warning("Please log in with Google to access the dashboard.")
        st.stop()

    st.header(f"Hello {st.user.name}")
    if hasattr(st.user, "picture"):
        st.image(st.user.picture)
    st.sidebar.subheader("User info")
    st.sidebar.json({k: v for k, v in st.user.__dict__.items() if not k.startswith('_')})
    st.divider()

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