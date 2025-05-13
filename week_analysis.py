from datetime import datetime
import yfinance as yf
import pandas as pd
from database import initialize_database, insert_daily_analysis, fetch_historical_prices
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

def save_weekly_analysis_to_csv(filename, analysis_results):
    """Save the weekly analysis results to a CSV file, avoiding duplicates."""
    try:
        existing_rows = set()

        # Read existing rows to avoid duplicates
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_rows.add((row['ticker'], row['start_date'], row['end_date']))
        except FileNotFoundError:
            pass  # File doesn't exist yet, so no duplicates to check

        # Write new rows, avoiding duplicates
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['ticker', 'average_close', 'start_date', 'end_date'])

            # Write the header only if the file is empty
            if file.tell() == 0:
                writer.writeheader()

            for result in analysis_results:
                if (result['ticker'], result['start_date'], result['end_date']) not in existing_rows:
                    writer.writerow(result)

        print(f"Weekly analysis results saved to {filename}.")
    except Exception as e:
        print(f"Failed to save weekly analysis results to CSV: {e}")

if __name__ == "__main__":
    tickers = ["PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3"]
    analysis_results = []

    for ticker in tickers:
        print(f"Analyzing weekly data for {ticker}...")
        result = analyze_weekly_data_from_db(ticker)
        if result:
            analysis_results.append(result)

    if analysis_results:
        save_weekly_analysis_to_csv("weekly_analysis.csv", analysis_results)