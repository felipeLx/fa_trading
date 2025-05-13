from datetime import datetime
import yfinance as yf
import pandas as pd
from database import initialize_database, insert_yearly_analysis
import time

max_retries = 5
retry_delay = 10  # seconds
initial_delay = 5  # seconds

# Step 1: Fetch Market Data
def fetch_data(tickers, start_date, end_date):
    """Fetch historical data for multiple tickers."""
    data = {}
    
    for attempt in range(max_retries):
        try:
            for ticker in tickers:
                print(f"Fetching data for {ticker}...")
                data[ticker] = yf.download(ticker, start=start_date, end=end_date)
            return data
        except yf.exceptions.YRateLimitError:
            print(f"Rate limit error encountered (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

# Update the main function to include database insertion
def main():
    tickers =["PETR4.SA"] #, "VALE3.SA", "ITUB4.SA", "AMER3.SA", "B3SA3.SA", "MGLU3.SA", "LREN3.SA", "ITSA4.SA", "BBAS3.SA", "RENT3.SA", "ABEV3.SA"]
    start_date = "2020-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    print(f"Fetching data for tickers: {', '.join(tickers)} from {start_date} to {end_date}...")
    data = fetch_data(tickers, start_date, end_date)

    # Initialize the database to ensure tables exist
    initialize_database()

    for ticker, df in data.items():
        print(f"\nData for {ticker}:")
        print(df.head())  # Display the first few rows of data for each ticker

        print(f"Inserting data into the database for {ticker}...")
        data_to_insert = [
            (
                ticker,
                row.name.strftime("%Y-%m-%d"),
                float(row['Close'])
            )
            for _, row in df.iterrows()
        ]
        insert_yearly_analysis(data_to_insert)

if __name__ == "__main__":
    main()