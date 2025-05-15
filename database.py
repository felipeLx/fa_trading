import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone
import numpy as np

# Load environment variables
load_dotenv()

"""Initialize the PostgreSQL database and create tables."""
SUPABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_KEY = os.getenv("DATABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def safe_check_nan(value):
    """Check if a value is NaN, safely handling non-numeric types."""
    if isinstance(value, (int, float, np.float64)):
        return np.isnan(value)
    return False

def insert_daily_analysis(data):
    """Insert data into the daily_analysis table."""
    date, close_price, short_ma, long_ma, rsi, macd, signal_line, ticker = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d')

    close_price = None if safe_check_nan(close_price) else close_price
    short_ma = None if safe_check_nan(short_ma) else short_ma
    long_ma = None if safe_check_nan(long_ma) else long_ma
    rsi = None if safe_check_nan(rsi) else rsi
    macd = None if safe_check_nan(macd) else macd
    signal_line = None if safe_check_nan(signal_line) else signal_line

    result = supabase.table("daily_analysis").insert(
        {"date": date, 
         "close_price": close_price, 
         "short_ma": short_ma, 
         "long_ma": long_ma, 
         "rsi": rsi, 
         "macd": macd, 
         "signal_line": signal_line, 
         "ticker": ticker, 
         "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted daily analysis data for {date}")
    else:
        print(f"Failed to insert daily analysis data for {date}")

def insert_yearly_analysis(data):
    """Insert data into the yearly_analysis table."""
    date, close_price, ticker = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d')
    result = supabase.table("yearly_analysis").insert(
        {"date": date, "close_price": close_price, "ticker": ticker, "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted yearly analysis data for {date}")
    else:
        print(f"Failed to insert yearly analysis data for {date}")

def save_balance_sheet_data(data):
    """Save balance sheet data and financial ratios to the database."""
    ticker, end_date, total_current_assets, total_current_liabilities, total_liabilities, total_stockholder_equity, current_ratio, debt_to_equity_ratio = data


    result = supabase.table("balance_sheet").insert(
        {"ticker": ticker, "end_date": end_date, "total_current_assets": total_current_assets, "total_current_liabilities": total_current_liabilities, "total_liabilities": total_liabilities, "total_stockholder_equity": total_stockholder_equity, "current_ratio": current_ratio, "debt_to_equity_ratio": debt_to_equity_ratio, "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted balance sheet data for {ticker} on {end_date}")
    else:
        print(f"Failed to insert balance sheet data for {ticker} on {end_date}")

def save_historical_prices(data):
    """Save historical prices to the database."""
    ticker, date, open_price, high_price, low_price, close_price, volume, adjusted_close = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d')
    result = supabase.table("historical_prices").insert(
        {"ticker": ticker, "date": date, "open": open_price, "high": high_price, "low": low_price, "close": close_price, "volume": volume, "adjusted_close": adjusted_close, "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted historical price data for {ticker} on {date}")
    else:
        print(f"Failed to insert historical price data for {ticker} on {date}")

def fetch_balance_sheet_data(ticker):
    """Fetch balance sheet data and financial ratios for a given ticker from the database."""
    data = supabase.table("balance_sheet").select(
        "id, ticker, end_date, total_current_assets, total_current_liabilities, total_liabilities, total_stockholder_equity, current_ratio, debt_to_equity_ratio"
    ).eq("ticker", ticker).order("end_date", desc=True).execute()

    if data.status_code == 200 and data.data:
        return data.data
    else:
        print(f"Failed to fetch balance sheet data for {ticker}: {data.error}")
        return None

def fetch_historical_prices(ticker):
    """Fetch historical prices for a given ticker from the database."""
    data = supabase.table("historical_prices").select(
        "id, ticker, date, open, high, low, close, volume, adjusted_close"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.status_code == 200 and data.data:
        return data.data
    else:
        print(f"Failed to fetch historical prices for {ticker}: {data.error}")
        return None

def fetch_daily_analysis(ticker):
    """Fetch daily analysis data for a given ticker from the database."""
    data = supabase.table("daily_analysis").select(
        "id, date, close_price, short_ma, long_ma, rsi, macd, signal_line"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.status_code == 200 and data.data:
        return data.data
    else:
        print(f"Failed to fetch daily analysis data for {ticker}: {data.error}")
        return None

def fetch_yearly_analysis(ticker):
    """Fetch yearly analysis data for a given ticker from the database."""
    data = supabase.table("yearly_analysis").select(
        "id, date, close_price, ticker"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.status_code == 200 and data.data:
        return data.data
    else:
        print(f"Failed to fetch yearly analysis data for {ticker}: {data.error}")
        return None

def insert_asset_analysis(data):
    """Insert analysis results into the asset_analysis table."""
    ticker, forward_pe, profit_margins, beta, dividend_yield, peg_ratio = data
    result = supabase.table("asset_analysis").insert({
        "ticker": ticker,
        "forward_pe": forward_pe,
        "profit_margins": profit_margins,
        "beta": beta,
        "dividend_yield": dividend_yield,
        "peg_ratio": peg_ratio,
        "user_id": os.getenv("USER_ID")
    }).execute()

    if result:
        print(f"Inserted asset analysis data for {ticker}.")
    else:
        print(f"Failed to insert asset analysis data for {ticker}")

def fetch_asset_analysis(ticker):
    """Fetch analysis results for a specific ticker from the asset_analysis table."""
    result = supabase.table("asset_analysis").select(
        "ticker, forward_pe, profit_margins, beta, dividend_yield, peg_ratio"
    ).eq("ticker", ticker).order("analysis_date", desc=True).execute()

    if result.status_code == 200 and result.data:
        return result.data
    else:
        print(f"Failed to fetch asset analysis data for {ticker}: {result.error}")
        return None
