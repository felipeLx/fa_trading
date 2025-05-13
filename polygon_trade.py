from polygon import RESTClient
from dotenv import load_dotenv
import os

load_dotenv()

client = RESTClient(os.getenv("POLYGON_API_KEY"))
"""

options_chain = []
for o in client.list_snapshot_options_chain(
    "HCP",
    params={
        "expiration_date.gte": "2025-06-16",
        "strike_price.gte": 29,
        "strike_price.lte": 30,
    },
):
    options_chain.append(o)

print(options_chain)
print(len(options_chain))
"""

ticker = "AAPL"

# List Aggregates (Bars)
aggs = []
for a in client.list_aggs(ticker=ticker, multiplier=1, timespan="minute", from_="2024-05-09", to="2025-05-09", limit=50000):
    aggs.append(a)

print(aggs)

# Get Last Trade
trade = client.get_last_trade(ticker=ticker)
print(trade)

# List Trades
trades = client.list_trades(ticker=ticker, timestamp="2025-05-09")
for trade in trades:
    print(trade)

# Get Last Quote
quote = client.get_last_quote(ticker=ticker)
print(quote)

# List Quotes
quotes = client.list_quotes(ticker=ticker, timestamp="2025-05-09")
for quote in quotes:
    print(quote)