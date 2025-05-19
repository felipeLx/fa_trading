import streamlit as st
import pandas as pd
from utils.database import fetch_daily_analysis, fetch_historical_prices, fetch_balance_sheet_data, fetch_asset_analysis
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import plotly.graph_objects as go



def main():
    st.title("InvestFal Dashboard")
   
    user = getattr(st, "user", None)
    #if not user:
     #   st.warning("You must be logged in to access this app.")
   #     st.stop()

    #st.sidebar.write(f"Logged in as: {user.email}")
        # Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Asset Overview", "See Charts", "Best Asset to Trade", "Run Robot"])

    if page == "Asset Overview":
        st.header("Asset Overview")
        tickers = ["PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3", "ITSA4", "RDOR3", "RAIZ4", "PETZ3", "PSSA3", "VBBR3"]
        selected_ticker = st.selectbox("Select Ticker:", tickers, index=0)
        st.subheader(f"Data for {selected_ticker}")
        st.write("### Balance Sheet Data")
        balance_sheet_data = fetch_balance_sheet_data(selected_ticker)
        if balance_sheet_data:
            st.dataframe(balance_sheet_data)
        else:
            st.write("No balance sheet data available.")
        
        st.write("### Asset Analysis Data")
        asset_analysis_data = fetch_asset_analysis(selected_ticker)
        if asset_analysis_data:
            st.dataframe(asset_analysis_data)
        else:
            st.write("No asset analysis data available.")
        
        st.write("### Daily Analysis Data")
        daily_analysis_data = fetch_daily_analysis(selected_ticker)
        if daily_analysis_data:
            daily_df = pd.DataFrame(daily_analysis_data)
            st.dataframe(daily_df)
        else:
            st.write("No daily analysis data available.")

        st.write("### Historical Prices and Indicators")
        historical_prices = fetch_historical_prices(selected_ticker)
        historical_prices = pd.DataFrame(historical_prices)
        st.dataframe(historical_prices)
        

    elif page == "See Charts":
        tickers = ["PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3", "ITSA4", "RDOR3", "RAIZ4", "PETZ3", "PSSA3", "VBBR3"]
        selected_ticker = st.selectbox("Select Ticker:", tickers, index=0)
        st.write("### Daily Analysis Line Chart")
        st.header(f"Charts for {selected_ticker}")

        daily_analysis_data = fetch_daily_analysis(selected_ticker)
        if daily_analysis_data:
            daily_df = pd.DataFrame(daily_analysis_data)
            st.write("Price and Moving Averages")
            st.line_chart(
                daily_df.set_index("date")[["close_price", "short_ma", "long_ma"]]
            )

            st.write("RSI")
            st.line_chart(
                daily_df.set_index("date")[["rsi"]]
            )

            st.write("MACD and Signal Line")
            st.line_chart(
                daily_df.set_index("date")[["macd", "signal_line"]]
            )
        else:
            st.write("No daily analysis data available.")

        st.write("### Historical Prices Line Chart")
        historical_prices = fetch_historical_prices(selected_ticker)
        if historical_prices:
            historical_prices = pd.DataFrame(historical_prices)
            # Check for required columns
            required_cols = {"date", "open", "high", "low", "close"}
            if required_cols.issubset(historical_prices.columns):
                historical_prices = historical_prices.sort_values("date")
                fig = go.Figure(data=[go.Candlestick(
                    x=historical_prices["date"],
                    open=historical_prices["open"],
                    high=historical_prices["high"],
                    low=historical_prices["low"],
                    close=historical_prices["close"]
                )])
                fig.update_layout(xaxis_title="Date", yaxis_title="Price", title="Candlestick Chart")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No suitable columns (open, high, low, close) for candlestick chart in historical prices data.")
        else:
            st.write("No historical price data available.")

    elif page == "Best Asset to Trade":
        st.header("Find the Best Asset to Trade")
        if st.button("Run Technical Analysis"):
            st.write("Running technical analysis to find the best asset...")
            # run_technical_analysis()
            st.success("Technical analysis completed. Check the database for results.")

    elif page == "Run Robot":
        st.header("Run Trading Robot")
        if st.button("Start Trading Robot"):
            st.write("Starting the trading robot...")
            account_balance = 10000  # Example account balance in R$
            risk_per_trade = 0.02  # Risk 2% of account balance per trade
            # monitor_and_trade(account_balance, risk_per_trade)
            st.success("Trading robot is running.")

if __name__ == "__main__":
    main()