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
    """Insert data into the daily_analysis table, avoiding duplicates by ticker and date."""
    date, close_price, short_ma, long_ma, rsi, macd, signal_line, ticker = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d')

    # Check for existing entry
    existing = supabase.table("daily_analysis").select("id").eq("ticker", ticker).eq("date", date).execute()
    if existing.data and len(existing.data) > 0:
        print(f"Daily analysis for {ticker} on {date} already exists. Skipping insert.")
        return

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
    """Insert data into the yearly_analysis table, avoiding duplicates by ticker and date."""
    date, close_price, ticker = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d')
    existing = supabase.table("yearly_analysis").select("id").eq("ticker", ticker).eq("date", date).execute()
    if existing.data and len(existing.data) > 0:
        print(f"Yearly analysis for {ticker} on {date} already exists. Skipping insert.")
        return
    result = supabase.table("yearly_analysis").insert(
        {"date": date, "close_price": close_price, "ticker": ticker, "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted yearly analysis data for {date}")
    else:
        print(f"Failed to insert yearly analysis data for {date}")

def save_balance_sheet_data(data):
    """Save balance sheet data and financial ratios to the database."""
    ticker, end_date, total_current_assets, total_current_liabilities, total_liabilities, total_stockholder_equity, current_ratio, debt_to_equity_ratio = data

    existing = supabase.table("balance_sheet").select("id").eq("ticker", ticker).eq("end_date", end_date).execute()

    if existing.data and len(existing.data) > 0:
        print(f"Balance sheet data for {ticker} on {end_date} already exists. Skipping insert.")
        return

    result = supabase.table("balance_sheet").insert(
        {
            "ticker": ticker,
            "end_date": end_date,
            "total_current_assets": total_current_assets,
            "total_current_liabilities": total_current_liabilities,
            "total_liabilities": total_liabilities,
            "total_stockholder_equity": total_stockholder_equity,
            "current_ratio": current_ratio,
            "debt_to_equity_ratio": debt_to_equity_ratio,
            "user_id": os.getenv("USER_ID")
        }
    ).execute()

    if result:
        print(f"Inserted balance sheet data for {ticker} on {end_date}")
    else:
        print(f"Failed to insert balance sheet data for {ticker} on {end_date}")


def save_historical_prices(data):
    """Save historical prices to the database, avoiding duplicates by ticker and date."""
    ticker, date, open_price, high_price, low_price, close_price, volume, adjusted_close = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d')
    existing = supabase.table("historical_prices").select("id").eq("ticker", ticker).eq("date", date).execute()
    if existing.data and len(existing.data) > 0:
        print(f"Historical price for {ticker} on {date} already exists. Skipping insert.")
        return
    result = supabase.table("historical_prices").insert(
        {"ticker": ticker, "date": date, "open": open_price, "high": high_price, "low": low_price, "close": close_price, "volume": volume, "adjusted_close": adjusted_close, "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted historical price data for {ticker} on {date}")
    else:
        print(f"Failed to insert historical price data for {ticker} on {date}")

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


def insert_finance_metrics(data):
    """Insert finance metrics into the finance_metrics table."""
    ticker, roe, roa, revenue_growth, operating_cashflow, free_cashflow, current_ratio, debt_to_equity, profit_margins, gross_margins, ebitda_margins, operating_margins, operating_cashflow_ratio, free_cash_flow_ratio = data
    result = supabase.table("finance_metrics").insert({
        "ticker": ticker,
        "roe": roe,
        "roa": roa,
        "revenue_growth": revenue_growth,
        "operating_cashflow": operating_cashflow,
        "free_cashflow": free_cashflow,
        "current_ratio": current_ratio,
        "debt_to_equity": debt_to_equity,
        "profit_margins": profit_margins,
        "gross_margins": gross_margins,
        "ebitda_margins": ebitda_margins,
        "operating_margins": operating_margins,
        "operating_cashflow_ratio": operating_cashflow_ratio,
        "free_cash_flow_ratio": free_cash_flow_ratio,
        "user_id": os.getenv("USER_ID")
    }).execute()

    if result:
        print(f"Inserted finance metrics data for {ticker}.")
    else:
        print(f"Failed to insert finance metrics data for {ticker}")

def insert_intraday_prices(data):
    """Insert intraday prices into the intraday_prices table."""
    ticker, date, open_price, high_price, low_price, close_price, volume, adjusted_close = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    existing = supabase.table("intraday_prices").select("id").eq("ticker", ticker).eq("date", date).execute()
    if existing.data and len(existing.data) > 0:
        print(f"Intraday price for {ticker} on {date} already exists. Skipping insert.")
        return
    result = supabase.table("intraday_prices").insert(
        {"ticker": ticker, "date": date, "open": open_price, "high": high_price, "low": low_price, "close": close_price, "volume": volume, "adjusted_close": adjusted_close, 
        "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted intraday price data for {ticker} on {date}")
    else:
        print(f"Failed to insert intraday price data for {ticker} on {date}")

def fetch_intraday_prices(ticker):
    """Fetch intraday prices for a given ticker from the database."""
    data = supabase.table("intraday_prices").select(
        "id, ticker, date, open, high, low, close, volume, adjusted_close"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch intraday prices for {ticker}")
        return None
    
def fetch_finance_metrics(ticker):
    """Fetch finance metrics for a given ticker from the database."""
    data = supabase.table("finance_metrics").select(
        "id, ticker, roe, roa, revenue_growth, operating_cashflow, free_cashflow, current_ratio, debt_to_equity, profit_margins, gross_margins, ebitda_margins, operating_margins, operating_cashflow_ratio, free_cash_flow_ratio"
    ).eq("ticker", ticker).order("created_at", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch finance metrics for {ticker}")
        return None

def fetch_balance_sheet_data(ticker):
    """Fetch balance sheet data and financial ratios for a given ticker from the database."""
    data = supabase.table("balance_sheet").select(
        "id, ticker, end_date, total_current_assets, total_current_liabilities, total_liabilities, total_stockholder_equity, current_ratio, debt_to_equity_ratio"
    ).eq("ticker", ticker).order("end_date", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch balance sheet data for {ticker}")
        return None

def fetch_historical_prices(ticker):
    """Fetch historical prices for a given ticker from the database."""
    data = supabase.table("historical_prices").select(
        "id, ticker, date, open, high, low, close, volume, adjusted_close"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch historical prices for {ticker}")
        return None

def fetch_daily_analysis(ticker):
    """Fetch daily analysis data for a given ticker from the database."""
    data = supabase.table("daily_analysis").select(
        "id, date, close_price, short_ma, long_ma, rsi, macd, signal_line"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch daily analysis data for {ticker}")
        return None

def fetch_yearly_analysis(ticker):
    """Fetch yearly analysis data for a given ticker from the database."""
    data = supabase.table("yearly_analysis").select(
        "id, date, close_price, ticker"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch yearly analysis data for {ticker}")
        return None

def fetch_asset_analysis(ticker):
    """Fetch analysis results for a specific ticker from the asset_analysis table."""
    result = supabase.table("asset_analysis").select(
        "ticker, forward_pe, profit_margins, beta, dividend_yield, peg_ratio"
    ).eq("ticker", ticker).order("created_at", desc=True).execute()

    if result.data:
        return result.data
    else:
        print(f"Failed to fetch asset analysis data for {ticker}")
        return None
