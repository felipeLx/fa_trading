from datetime import datetime
import yfinance as yf
import pandas as pd
from database import insert_daily_analysis, insert_yearly_analysis, save_balance_sheet_data, save_historical_prices, insert_asset_analysis
import time
import requests
from dotenv import load_dotenv
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from asset_analysis import analyze_asset
import numpy as np

load_dotenv()

max_retries = 5
retry_delay = 10  # seconds
initial_delay = 5  # seconds

def calculate_moving_averages(data, short_window=20, long_window=50):
    """Calculate short and long moving averages."""
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    return data

def identify_signals(data):
    """Identify buy and sell signals based on moving average crossovers."""
    data['Signal'] = 0
    data.loc[data['Short_MA'] > data['Long_MA'], 'Signal'] = 1  # Buy signal
    data.loc[data['Short_MA'] <= data['Long_MA'], 'Signal'] = -1  # Sell signal
    return data

def fetch_market_and_balance_sheet_data(ticker):
    """Fetch market and balance sheet data for a given ticker."""
    token = os.getenv('BRAPI_API_KEY')
    if not token:
        print("Error: BRAPI_API_KEY is not set in the environment variables.")
        return None

    url = f"https://brapi.dev/api/quote/{ticker}"
    params = {
        'range': '1mo',
        'interval': '90m',
        'fundamental': 'true',
        'dividends': 'true',
        'modules': 'balanceSheetHistory',
        'token': token,
    }

    try:
        response = requests.get(url, params=params)
        print(f"Requesting URL: {response.url}")  # Print the full URL with parameters
        print(f"Response Status Code: {response.status_code}")
        print(response.text)  # Print the response text for debugging
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Request failed with status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data for {ticker}: {e}")
        return None

def process_market_and_balance_sheet_data(data):
    """Process market, balance sheet, and historical price data."""
    try:
        market_data = data['results'][0]  # Use the latest market data
        balance_sheet_data = data['results'][0]['balanceSheetHistory'][0]  # Use the most recent balance sheet
        historical_data = data['results'][0]['historicalDataPrice'][-26:]  # Use the last 5 days of historical data

        # Extract relevant market data 
        market_info = {
            'symbol': market_data['symbol'],
            'regularMarketPrice': market_data['regularMarketPrice'],
            'regularMarketVolume': market_data['regularMarketVolume'],
            'fiftyTwoWeekRange': market_data['fiftyTwoWeekRange'],
            'priceEarnings': market_data.get('priceEarnings'),
            'earningsPerShare': market_data.get('earningsPerShare')
        }

        # Extract relevant balance sheet data
        balance_sheet_info = {
            'endDate': balance_sheet_data['endDate'],
            'totalCurrentAssets': balance_sheet_data['totalCurrentAssets'],
            'totalCurrentLiabilities': balance_sheet_data['totalCurrentLiabilities'],
            'totalLiab': balance_sheet_data['totalLiab'],
            'totalStockholderEquity': balance_sheet_data['totalStockholderEquity']
        }

        # Extract relevant historical price data
        historical_prices = [
            {
                'date': hp['date'],
                'open': hp['open'],
                'high': hp['high'],
                'low': hp['low'],
                'close': hp['close'],
                'volume': hp['volume'],
                'adjustedClose': hp['adjustedClose']
            }
            for hp in historical_data
        ]

        return market_info, balance_sheet_info, historical_prices
    except KeyError as e:
        print(f"Missing key in data: {e}")
        return None, None, None

def calculate_financial_ratios(balance_sheet_data):
    """Calculate financial ratios from balance sheet data."""
    try:
        current_ratio = balance_sheet_data['totalCurrentAssets'] / balance_sheet_data['totalCurrentLiabilities']
        debt_to_equity_ratio = balance_sheet_data['totalLiab'] / balance_sheet_data['totalStockholderEquity']
        return {
            'current_ratio': current_ratio,
            'debt_to_equity_ratio': debt_to_equity_ratio
        }
    except KeyError as e:
        print(f"Missing key in balance sheet data: {e}")
        return {}

def prepare_features_and_labels(data, market_info, financial_ratios):
    """Prepare features and labels for machine learning."""
    features = []
    labels = []

    for row in data:
        features.append([
            row['regularMarketPrice'],
            row['regularMarketVolume'],
            financial_ratios.get('current_ratio', 0),
            financial_ratios.get('debt_to_equity_ratio', 0)
        ])
        labels.append(1 if row['regularMarketPrice'] > row['regularMarketOpen'] else 0)  # 1 for profit, 0 for loss

    return features, labels

def train_model(features, labels):
    """Train a machine learning model to predict the best asset."""
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.2f}")

    # Save the trained model
    joblib.dump(model, 'daytrade_model.pkl')
    return model

def predict_best_asset(model, features, tickers):
    """Predict the best asset for day trading."""
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1]  # Probability of class 1 (profit)

    best_asset_index = probabilities.argmax()
    best_asset = tickers[best_asset_index]
    print(f"Best asset to trade: {best_asset}")
    return best_asset

def calculate_stop_loss_take_profit_levels(historical_prices):
    """Calculate stop-loss and take-profit levels based on historical prices."""
    lowest_low = min(hp['low'] for hp in historical_prices)
    highest_high = max(hp['high'] for hp in historical_prices)

    stop_loss = lowest_low * 0.99  # Slightly below the lowest low
    take_profit = highest_high * 1.01  # Slightly above the highest high

    return stop_loss, take_profit

def calculate_position_size(account_balance, risk_per_trade, stop_loss, current_price):
    """Calculate the position size based on account balance, risk, and stop-loss distance."""
    risk_amount = account_balance * risk_per_trade
    stop_loss_distance = current_price - stop_loss
    if stop_loss_distance <= 0:
        raise ValueError("Stop-loss distance must be positive.")
    position_size = risk_amount / stop_loss_distance
    return position_size

def apply_stop_loss_take_profit(current_price, stop_loss, take_profit):
    """Check if stop-loss or take-profit conditions are met."""
    if current_price <= stop_loss:
        return "stop_loss"
    elif current_price >= take_profit:
        return "take_profit"
    return None

def save_financial_data_to_db(ticker, balance_sheet_info, financial_ratios):
    """Save balance sheet data and financial ratios to the database."""
    try:
        save_balance_sheet_data(
            ticker=ticker,
            end_date=balance_sheet_info['endDate'],
            total_current_assets=balance_sheet_info['totalCurrentAssets'],
            total_current_liabilities=balance_sheet_info['totalCurrentLiabilities'],
            total_liabilities=balance_sheet_info['totalLiab'],
            total_stockholder_equity=balance_sheet_info['totalStockholderEquity'],
            current_ratio=financial_ratios.get('current_ratio'),
            debt_to_equity_ratio=financial_ratios.get('debt_to_equity_ratio')
        )
        print(f"Saved financial data for {ticker} to the database.")
    except Exception as e:
        print(f"Failed to save financial data for {ticker}: {e}")

def save_historical_prices_to_db(ticker, historical_prices):
    """Save historical prices to the database."""
    try:
        save_historical_prices(ticker, historical_prices)
        print(f"Saved historical prices for {ticker} to the database.")
    except Exception as e:
        print(f"Failed to save historical prices for {ticker}: {e}")

def calculate_rsi(prices, period=14):
    """Calculate the Relative Strength Index (RSI)."""
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.convolve(gains, np.ones(period) / period, mode='valid')
    avg_loss = np.convolve(losses, np.ones(period) / period, mode='valid')

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return np.concatenate((np.full(period - 1, np.nan), rsi))

def calculate_macd(prices, short_period=12, long_period=26, signal_period=9):
    """Calculate MACD and Signal Line."""
    short_ema = pd.Series(prices).ewm(span=short_period, adjust=False).mean()
    long_ema = pd.Series(prices).ewm(span=long_period, adjust=False).mean()

    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()

    return macd, signal_line

def main():
    tickers = ["PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3", "ITSA4", "RDOR3", "RAIZ4", "PETZ3", "PSSA3", "VBBR3"]

    all_features = []
    all_labels = []

    for ticker in tickers:
        print(f"Fetching market and balance sheet data for {ticker}...")
        market_data = fetch_market_and_balance_sheet_data(ticker)

        if market_data:
            print(f"Processing data for {ticker}...")
            market_info, balance_sheet_info, historical_prices = process_market_and_balance_sheet_data(market_data)

            if market_info and balance_sheet_info and historical_prices:
                print(f"Calculating financial ratios for {ticker}...")
                financial_ratios = calculate_financial_ratios(balance_sheet_info)

                print(f"Saving financial data for {ticker} to the database...")
                save_balance_sheet_data((
                    ticker,
                    balance_sheet_info['endDate'],
                    balance_sheet_info['totalCurrentAssets'],
                    balance_sheet_info['totalCurrentLiabilities'],
                    balance_sheet_info['totalLiab'],
                    balance_sheet_info['totalStockholderEquity'],
                    financial_ratios.get('current_ratio'),
                    financial_ratios.get('debt_to_equity_ratio')
                ))

                print(f"Saving historical prices for {ticker} to the database...")
                for price in historical_prices:
                    save_historical_prices((
                        ticker,
                        price['date'],
                        price['open'],
                        price['high'],
                        price['low'],
                        price['close'],
                        price['volume'],
                        price['adjustedClose']
                    ))

                print(f"Saving daily analysis for {ticker} to the database...")
                close_prices = [p['close'] for p in historical_prices]

                # Calculate RSI, MACD, and Signal Line
                rsi_values = calculate_rsi(close_prices)
                macd_values, signal_line_values = calculate_macd(close_prices)

                for i, price in enumerate(historical_prices):
                    # Calculate short_ma and long_ma using moving averages
                    short_ma = sum(close_prices[max(0, i-2):i+1]) / min(3, i+1)  # Example: 3-period moving average
                    long_ma = sum(close_prices[:i+1]) / (i+1)  # Example: cumulative moving average

                    rsi = rsi_values[i] if i < len(rsi_values) else None
                    macd = macd_values[i] if i < len(macd_values) else None
                    signal_line = signal_line_values[i] if i < len(signal_line_values) else None

                    insert_daily_analysis((
                        ticker,
                        price['date'],
                        price['close'],
                        short_ma,
                        long_ma,
                        rsi,
                        macd,
                        signal_line
                    ))

                print(f"Saving yearly analysis for {ticker} to the database...")
                insert_yearly_analysis((
                    historical_prices[0]['date'],  # Most recent date
                    historical_prices[0]['close'],  # Most recent close price
                    ticker,
                ))

                print(f"Analyzing asset for {ticker}...")
                asset_analysis = analyze_asset(market_data['results'][0]['defaultKeyStatistics'], market_info['regularMarketPrice'])
                insert_asset_analysis((
                    ticker,
                    asset_analysis['forward_pe'],
                    asset_analysis['profit_margins'],
                    asset_analysis['beta'],
                    asset_analysis['dividend_yield'],
                    asset_analysis['peg_ratio']
                ))

                print(f"Preparing features and labels for {ticker}...")
                features, labels = prepare_features_and_labels(market_data['results'], market_info, financial_ratios)
                all_features.extend(features)
                all_labels.extend(labels)

    print("Training the model...")
    model = train_model(all_features, all_labels)

    print("Predicting the best asset for day trading...")
    predict_best_asset(model, all_features, tickers)

if __name__ == "__main__":
    main()