from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv('keys.env')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

client = MongoClient("mongodb://localhost:27017/")
db = client["the-market-collector"]
stocks_collection = db["market-collection"]

def get_latest_stocks(limit=50):
    """Retrieve latest stock records from MongoDB"""
    try:
        return list(stocks_collection.find().sort("timestamp", -1).limit(limit))
    except Exception as e:
        logger.error(f"📦 Database query failed: {str(e)}")
        return []

def fetch_stocks():
    symbol = "TSLA"
    all_stocks_data = []
    
    logger.info(f"🌐 Attempting to fetch stock data for {symbol}...")
    api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        
        data = response.json().get("Time Series (5min)")
        if not data:
            logger.error(f"❌ Received empty data set for {symbol} from API")
            return []
            
        logger.debug(f"📦 Raw API response: {response.text[:100]}...")
            
        for timestamp, stock_data in data.items():
            stock_record = {
                "symbol": symbol,
                "timestamp": timestamp,
                "open": float(stock_data["1. open"]),
                "high": float(stock_data["2. high"]),
                "low": float(stock_data["3. low"]),
                "close": float(stock_data["4. close"]),
                "volume": int(stock_data["5. volume"])
            }
            all_stocks_data.append(stock_record)
            
        logger.info(f"✅ Successfully fetched {len(all_stocks_data)} records for {symbol}")
        return all_stocks_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"🚨 API request failed: {str(e)}")
        return []
    except KeyError as e:
        logger.error(f"🔍 Unexpected API response format: {str(e)}")
        return []

def store_stocks(stocks_data):
    if not stocks_data:
        logger.warning("⚠️ No stock data received for storage")
        return
    
    try:
        count = 0
        duplicates = 0
        for stock in stocks_data:
            if not stocks_collection.find_one({"symbol": stock["symbol"], "timestamp": stock["timestamp"]}):
                stocks_collection.insert_one(stock)
                count += 1
            else:
                duplicates += 1
                
        logger.info(f"💾 Storage complete: {count} new records, {duplicates} duplicates skipped")
        return count
    except Exception as e:
        logger.error(f"🔥 Database operation failed: {str(e)}")
        return 0
