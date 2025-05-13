import sqlite3

def initialize_database():
    """Initialize the SQLite database and create tables in airflow.db."""
    conn = sqlite3.connect('/mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/airflow/airflow.db')
    cursor = conn.cursor()

    # Create a table for daily analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            close_price REAL NOT NULL,
            short_ma REAL,
            long_ma REAL,
            rsi REAL,
            macd REAL,
            signal_line REAL
        )
    ''')

    # Create a table for yearly analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS yearly_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            close_price REAL NOT NULL
        )
    ''')

    # Create a table for balance sheet data if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS balance_sheet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            end_date TEXT NOT NULL,
            total_current_assets REAL,
            total_current_liabilities REAL,
            total_liabilities REAL,
            total_stockholder_equity REAL,
            current_ratio REAL,
            debt_to_equity_ratio REAL
        )
    ''')

    # Create a table for historical prices if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            adjusted_close REAL
        )
    ''')

    conn.commit()
    conn.close()

def insert_daily_analysis(data):
    """Insert data into the daily_analysis table in airflow.db."""
    conn = sqlite3.connect('/mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/airflow/airflow.db')
    cursor = conn.cursor()

    cursor.executemany('''
        INSERT INTO daily_analysis (ticker, date, close_price, short_ma, long_ma, rsi, macd, signal_line)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)

    conn.commit()
    conn.close()

def insert_yearly_analysis(data):
    """Insert data into the yearly_analysis table in airflow.db."""
    conn = sqlite3.connect('/mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/airflow/airflow.db')
    cursor = conn.cursor()

    cursor.executemany('''
        INSERT INTO yearly_analysis (ticker, date, close_price)
        VALUES (?, ?, ?)
    ''', data)

    conn.commit()
    conn.close()

def save_balance_sheet_data(ticker, end_date, total_current_assets, total_current_liabilities, total_liabilities, total_stockholder_equity, current_ratio, debt_to_equity_ratio):
    """Save balance sheet data and financial ratios to the database."""
    conn = sqlite3.connect('/mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/airflow/airflow.db')
    cursor = conn.cursor()

    # Insert the data into the table
    cursor.execute('''
        INSERT INTO balance_sheet (
            ticker, end_date, total_current_assets, total_current_liabilities, total_liabilities, total_stockholder_equity, current_ratio, debt_to_equity_ratio
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ticker, end_date, total_current_assets, total_current_liabilities, total_liabilities, total_stockholder_equity, current_ratio, debt_to_equity_ratio))

    conn.commit()
    conn.close()

def fetch_balance_sheet_data(ticker):
    """Fetch balance sheet data and financial ratios for a given ticker from the database."""
    conn = sqlite3.connect('/mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/airflow/airflow.db')
    cursor = conn.cursor()

    # Query the balance sheet data for the given ticker
    cursor.execute('''
        SELECT end_date, total_current_assets, total_current_liabilities, total_liabilities, total_stockholder_equity, current_ratio, debt_to_equity_ratio
        FROM balance_sheet
        WHERE ticker = ?
        ORDER BY end_date DESC
        LIMIT 1
    ''', (ticker,))

    row = cursor.fetchone()
    conn.close()

    if (row):
        return {
            'end_date': row[0],
            'total_current_assets': row[1],
            'total_current_liabilities': row[2],
            'total_liabilities': row[3],
            'total_stockholder_equity': row[4],
            'current_ratio': row[5],
            'debt_to_equity_ratio': row[6]
        }
    return None

def save_historical_prices(ticker, historical_prices):
    """Save historical prices to the database."""
    conn = sqlite3.connect('/mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/airflow/airflow.db')
    cursor = conn.cursor()

    # Create a table for historical prices if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            adjusted_close REAL
        )
    ''')

    # Insert historical prices into the table
    for price in historical_prices:
        cursor.execute('''
            INSERT INTO historical_prices (ticker, date, open, high, low, close, volume, adjusted_close)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, price['date'], price['open'], price['high'], price['low'], price['close'], price['volume'], price['adjustedClose']))

    conn.commit()
    conn.close()

def fetch_historical_prices(ticker):
    """Fetch historical prices for a given ticker from the database."""
    conn = sqlite3.connect('/mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/airflow/airflow.db')
    cursor = conn.cursor()

    # Query the historical prices for the given ticker
    cursor.execute('''
        SELECT date, open, high, low, close, volume, adjusted_close
        FROM historical_prices
        WHERE ticker = ?
        ORDER BY date DESC
        LIMIT 5
    ''', (ticker,))

    rows = cursor.fetchall()
    conn.close()

    if rows:
        return [
            {
                'date': row[0],
                'open': row[1],
                'high': row[2],
                'low': row[3],
                'close': row[4],
                'volume': row[5],
                'adjusted_close': row[6]
            }
            for row in rows
        ]
    return None

if __name__ == "__main__":
    initialize_database()