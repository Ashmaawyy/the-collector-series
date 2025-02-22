from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import datetime
from dotenv import load_dotenv
import os

# Load environment variables from keys.env
load_dotenv('keys.env')

# Get the API key from the environment variable
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

app = Flask(__name__)

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-market-collector"]
stocks_collection = db["market-collection"]

def fetch_and_store_stocks():
    api_key = ALPHA_VANTAGE_API_KEY
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]  # Add more stock symbols as needed
    for symbol in symbols:
        api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&apikey={api_key}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json().get("Time Series (60min)", {})
            for timestamp, stock_data in data.items():
                if not stocks_collection.find_one({"symbol": symbol, "timestamp": timestamp}):
                    stocks_collection.insert_one({
                        "symbol": symbol,
                        "timestamp": timestamp,
                        "open": stock_data["1. open"],
                        "high": stock_data["2. high"],
                        "low": stock_data["3. low"],
                        "close": stock_data["4. close"],
                        "volume": stock_data["5. volume"]
                    })
            print(f"Stock data for {symbol} updated!")
        else:
            print(f"Failed to fetch stock data for {symbol}.")

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store_stocks, "interval", minutes=5)
scheduler.start()

@app.route('/')
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 5
    total_count = stocks_collection.count_documents({})
    total_pages = (total_count + per_page - 1) // per_page
    
    stocks = list(stocks_collection.find().sort("timestamp", -1).skip((page - 1) * per_page).limit(per_page))
    
    return render_template("index.html", stocks=stocks, page=page, total_pages=total_pages)

@app.route('/update_stocks', methods=['GET'])
def update_stocks():
    fetch_and_store_stocks()
    return jsonify({"status": "success", "message": "Stock data updated!"})

@app.route('/load_latest_stocks')
def load_latest_stocks():
    latest_stocks = list(stocks_collection.find().sort("timestamp", -1).limit(5))

    stocks_data = [
        {
            "symbol": item["symbol"],
            "timestamp": item["timestamp"],
            "open": item["open"],
            "high": item["high"],
            "low": item["low"],
            "close": item["close"],
            "volume": item["volume"]
        } for item in latest_stocks
    ]

    return jsonify({"stocks": stocks_data})

@app.route('/load_more_stocks')
def load_more_stocks():
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Load more stocks per scroll

    stocks = list(stocks_collection.find().sort("timestamp", -1).skip((page - 1) * per_page).limit(per_page))

    stocks_data = [
        {
            "symbol": item["symbol"],
            "timestamp": item["timestamp"],
            "open": item["open"],
            "high": item["high"],
            "low": item["low"],
            "close": item["close"],
            "volume": item["volume"]
        } for item in stocks
    ]

    return jsonify({"stocks": stocks_data, "page": page})

@app.route('/search_stocks')
def search_stocks():
    query = request.args.get("q", "").upper()
    stocks = list(stocks_collection.find({"symbol": {"$regex": query, "$options": "i"}}).limit(10))

    stocks_data = [
        {
            "symbol": item["symbol"],
            "timestamp": item["timestamp"],
            "open": item["open"],
            "high": item["high"],
            "low": item["low"],
            "close": item["close"],
            "volume": item["volume"]
        } for item in stocks
    ]

    return jsonify({"stocks": stocks_data})

if __name__ == "__main__":
    app.run(debug=True)
