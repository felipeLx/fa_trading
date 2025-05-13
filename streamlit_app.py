import streamlit as st
import sqlite3
import pandas as pd
from database import fetch_historical_prices, fetch_balance_sheet_data

def authenticate_user(username, password):
    """Simple authentication function."""
    # Replace this with a more secure authentication mechanism
    valid_users = {
        "admin": "password123",
        "user": "userpass"
    }
    return valid_users.get(username) == password

def fetch_table_data(table_name):
    """Fetch all data from a given table in the database."""
    conn = sqlite3.connect('/mnt/c/Users/USUARIO/Desktop/workspace/invest_fal/airflow/airflow.db')
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def main():
    st.title("InvestFal Dashboard")

    # Login Section
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if authenticate_user(username, password):
            st.sidebar.success("Login successful!")

            # Navigation
            st.sidebar.title("Navigation")
            page = st.sidebar.radio("Go to", ["Balance Sheet Data", "Historical Prices", "Charts"])

            if page == "Balance Sheet Data":
                st.header("Balance Sheet Data")
                df = fetch_table_data("balance_sheet")
                st.dataframe(df)

            elif page == "Historical Prices":
                st.header("Historical Prices")
                df = fetch_table_data("historical_prices")
                st.dataframe(df)

            elif page == "Charts":
                st.header("Charts")
                df = fetch_table_data("historical_prices")

                # Example: Plot average close price per ticker
                avg_close = df.groupby("ticker")["close"].mean().reset_index()
                st.bar_chart(avg_close.set_index("ticker"))
        else:
            st.sidebar.error("Invalid username or password")

if __name__ == "__main__":
    main()
