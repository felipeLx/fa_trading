import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yfinance as yf
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from strategy import calculate_moving_averages, calculate_rsi, calculate_macd, generate_signals
from order_execution import place_order
from database import initialize_database, insert_daily_analysis
from technical_analysis import main as recommend_asset, calculate_stop_loss_take_profit_levels, calculate_position_size, apply_stop_loss_take_profit

load_dotenv()

def send_email(subject, body):
    """Send an email notification."""
    sender_email = os.environ.get('GMAIL')  
    sender_password = os.environ.get('PASS')
    receiver_email = os.environ.get('GMAIL') 

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def fetch_realtime_data(ticker):
    """Fetch real-time data for a given ticker."""
    data = yf.download(ticker, period="1d", interval="1m")
    return data

def monitor_and_trade():
    """Monitor and trade the recommended asset."""
    # Step 1: Get the recommended asset from technical_analysis
    print("Fetching recommended asset...")
    recommended_asset, historical_prices = recommend_asset()  # Assuming `main` now returns the best asset and historical prices

    if not recommended_asset or not historical_prices:
        print("No recommended asset or historical data found. Exiting.")
        return

    print(f"Recommended asset for trading: {recommended_asset}")

    # Calculate stop-loss and take-profit levels using historical prices
    stop_loss, take_profit = calculate_stop_loss_take_profit_levels(historical_prices)
    print(f"Stop-loss: {stop_loss}, Take-profit: {take_profit}")

    # Step 2: Monitor the recommended asset in real-time
    while True:
        print(f"Fetching real-time data for {recommended_asset}...")
        data = fetch_realtime_data(recommended_asset)

        if data.empty:
            print(f"No data found for {recommended_asset}. Retrying...")
            time.sleep(300)  # Wait 5 minutes before retrying
            continue

        # Step 3: Apply strategy and risk management
        print("Calculating indicators...")
        data = calculate_moving_averages(data)
        data = calculate_rsi(data)
        data = calculate_macd(data)
        data = generate_signals(data)

        signal = data['Signal'].iloc[-1]
        current_price = data['Close'].iloc[-1]

        print(f"Signal: {signal}, Current Price: {current_price}")

        if signal == 1:  # Buy signal
            print("Buy signal detected. Calculating position size...")
            position_size = calculate_position_size(account_balance, risk_per_trade, stop_loss)
            place_order(api_key="your_api_key_here", ticker=recommended_asset, action="buy", quantity=position_size)
            apply_stop_loss_take_profit(current_price, stop_loss, take_profit)
            insert_daily_analysis(recommended_asset, "buy", position_size, current_price, stop_loss, take_profit)
            send_email("Trade Executed", f"Bought {position_size} of {recommended_asset} at {current_price}")
        elif signal == -1:  # Sell signal
            print("Sell signal detected. Executing sell order...")
            place_order(api_key="your_api_key_here", ticker=recommended_asset, action="sell", quantity=10)  # Example quantity
            insert_daily_analysis(recommended_asset, "sell", 10, current_price, stop_loss, take_profit)
            send_email("Trade Executed", f"Sold {recommended_asset} at {current_price}")

        print("Waiting for the next check...")
        time.sleep(300)  # Wait 5 minutes before the next check

def balance_and_risk_management():
    """Check account balance and apply risk management."""
    account_balance = 10000  # Example account balance in R$
    risk_per_trade = 0.02  # Risk 2% of account balance per trade

    return account_balance, risk_per_trade
if __name__ == "__main__":
    account_balance, risk_per_trade = balance_and_risk_management()

    # Initialize the database to ensure tables exist
    initialize_database()

    # Start monitoring and trading
    monitor_and_trade()