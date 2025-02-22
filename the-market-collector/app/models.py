from pymongo import MongoClient
from datetime import datetime

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-market-collector"]
stocks_collection = db["market-stocks"]

def store_stocks(stocks):
    """
    Stores stock market data in MongoDB with the new data structure.
    """
    formatted_stocks = []

    for stock in stocks:
        data = {
            "symbol": stock.get("symbol", "N/A"),
            "timestamp": stock.get("timestamp", datetime.utcnow()),  # Default to now if missing
            "open": stock.get("open", "N/A"),
            "high": stock.get("high", "N/A"),
            "low": stock.get("low", "N/A"),
            "close": stock.get("close", "N/A"),
            "volume": stock.get("volume", "N/A")
        }
        formatted_stocks.append(data)

    if formatted_stocks:
        stocks_collection.insert_many(formatted_stocks)
        print(f"✅ Successfully inserted {len(formatted_stocks)} stocks into MongoDB.")
    else:
        print(f"⚠ No valid stocks to insert.")

def get_latest_stocks(limit=50):
    """
    Fetches the latest stock market data from MongoDB.
    Returns a list of structured stocks sorted by timestamp.
    """
    latest_stocks = list(
        stocks_collection.find({}, {"_id": 0})  # Exclude MongoDB _id field
        .sort("timestamp", -1)  # Sort by latest timestamp
        .limit(limit)  # Limit results
    )

    return latest_stocks
