from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import requests
import os


# Load environment variables from keys.env
load_dotenv('C:/Users/ALDEYAA/OneDrive - AL DEYAA MEDIA PRODUCTION/Documents/the-collector-series/keys.env')

# Get the API key from the environment variable
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-market-collector"]
stocks_collection = db["market-collection"]

def fetch_stocks():
    """
    Fetches stock data from Alpha Vantage API.
    """
    api_key = ALPHA_VANTAGE_API_KEY
    symbols = ["GOOGL", "MSFT", "AMZN", "TSLA"]  # Add more stock symbols as needed
    all_stocks_data = []

    for symbol in symbols:
        api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&apikey={api_key}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json().get("Time Series (60min)", {})
            for timestamp, stock_data in data.items():
                stock_record = {
                    "symbol": symbol,
                    "timestamp": timestamp,
                    "open": stock_data["1. open"],
                    "high": stock_data["2. high"],
                    "low": stock_data["3. low"],
                    "close": stock_data["4. close"],
                    "volume": stock_data["5. volume"]
                }
                all_stocks_data.append(stock_record)
        else:
            print(f"❌ Failed to fetch data for {symbol}. Status code: {response.status_code}")
        
        # Add a delay to avoid hitting the API rate limit
        time.sleep(12)  # 12 seconds delay to stay within the free tier limit of 5 requests per minute

    if not all_stocks_data:
        print("❌ No stock data fetched.")
        return []
    else:
        print(f"✅ Successfully fetched {len(all_stocks_data)} records.")
        return all_stocks_data


def store_stocks(stocks_data):
    """
    Stores fetched stock data in MongoDB.
    """
    if not stocks_data:
        print("❌ No stock data to store.")
        return
    else:
        for stock in stocks_data:
            if not stocks_collection.find_one({"symbol": stock["symbol"], "timestamp": stock["timestamp"]}):
                stocks_collection.insert_one(stock)
        print(f"✅ Successfully stored {len(stocks_data)} stock records in MongoDB.")
