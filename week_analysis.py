from datetime import datetime
import yfinance as yf
import pandas as pd
from database import insert_daily_analysis, fetch_historical_prices
import time
import csv

max_retries = 5
retry_delay = 10  # seconds
initial_delay = 5  # seconds

def analyze_weekly_data_from_db(ticker):
    """Fetch historical prices from the database and perform weekly analysis."""
    historical_prices = fetch_historical_prices(ticker)

    if not historical_prices:
        print(f"No historical prices found for {ticker} in the database.")
        return None

    # Example analysis: Calculate average close price for the week
    average_close = sum(price['close'] for price in historical_prices) / len(historical_prices)
    return {
        'ticker': ticker,
        'average_close': average_close,
        'start_date': historical_prices[-1]['date'],
        'end_date': historical_prices[0]['date']
    }

def save_weekly_analysis_to_db(analysis_results):
    """Save the weekly analysis results to the database."""
    for result in analysis_results:
        try:
            # Prepare data for insertion
            data = (
                result['ticker'],
                result['end_date'],
                result['average_close'],
                None,  # Placeholder for short_ma
                None,  # Placeholder for long_ma
                None,  # Placeholder for rsi
                None,  # Placeholder for macd
                None   # Placeholder for signal_line
            )

            # Insert into the database using insert_daily_analysis
            insert_daily_analysis(data)
            print(f"Inserted weekly analysis data for {result['ticker']} into the database.")
        except Exception as e:
            print(f"Failed to insert weekly analysis data for {result['ticker']}: {e}")

if __name__ == "__main__":
    tickers = ["PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3"]
    analysis_results = []

    for ticker in tickers:
        print(f"Analyzing weekly data for {ticker}...")
        result = analyze_weekly_data_from_db(ticker)
        if result:
            analysis_results.append(result)

    if analysis_results:
        save_weekly_analysis_to_db(analysis_results)