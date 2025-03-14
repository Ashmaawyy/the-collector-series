import logging
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv('keys.env')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-market-collector"]
stocks_collection = db["market-collection"]

def fetch_stocks():
    """
    Fetches stock data from Alpha Vantage API.
    """
    symbol = "TSLA"
    all_stocks_data = []
    
    api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json().get("Time Series (5min)")
        if not data:
            logging.error(f"❌ No data fetched for {symbol}.")
        else:
            logging.info(f"✅ Successfully fetched data for {symbol}.")
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
        logging.error(f"❌ Failed to fetch data for {symbol}. Status code: {response.status_code}")
    
    if not all_stocks_data:
        logging.error("❌ No stock data fetched.")
        return []
    else:
        logging.info(f"✅ Successfully fetched {len(all_stocks_data)} records for {symbol}.")
        return all_stocks_data

def store_stocks(stocks_data):
    """
    Stores fetched stock data in MongoDB.
    """
    if not stocks_data:
        logging.error("❌ No stock data to store.")
        return
    else:
        count = 0
        for stock in stocks_data:
            if not stocks_collection.find_one({"symbol": stock["symbol"], "timestamp": stock["timestamp"]}):
                stocks_collection.insert_one(stock)
                count += 1
        logging.info(f"✅ Successfully stored {count} new stock records in MongoDB.")
        return
