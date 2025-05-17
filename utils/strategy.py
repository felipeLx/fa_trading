import pandas as pd

def calculate_moving_averages(data, short_window=20, long_window=50):
    """Calculate short and long moving averages."""
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    return data

def calculate_rsi(data, window=14):
    """Calculate Relative Strength Index (RSI)."""
    delta = data['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    """Calculate MACD and Signal Line."""
    data['MACD'] = data['Close'].ewm(span=short_window, adjust=False).mean() - data['Close'].ewm(span=long_window, adjust=False).mean()
    data['Signal_Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()
    return data

def generate_signals(data):
    """Generate buy/sell signals based on indicators."""
    data['Signal'] = 0

    # Moving Average Crossover
    data.loc[data['Short_MA'] > data['Long_MA'], 'Signal'] = 1  # Buy
    data.loc[data['Short_MA'] <= data['Long_MA'], 'Signal'] = -1  # Sell

    # RSI Overbought/Oversold
    data.loc[data['RSI'] < 30, 'Signal'] = 1  # Buy
    data.loc[data['RSI'] > 70, 'Signal'] = -1  # Sell

    # MACD Crossover
    data.loc[data['MACD'] > data['Signal_Line'], 'Signal'] = 1  # Buy
    data.loc[data['MACD'] <= data['Signal_Line'], 'Signal'] = -1  # Sell

    return data

def calculate_position_size(account_balance, risk_per_trade, stop_loss_distance):
    """Calculate the position size based on account balance and risk management rules."""
    risk_amount = account_balance * risk_per_trade
    position_size = risk_amount / stop_loss_distance
    return position_size