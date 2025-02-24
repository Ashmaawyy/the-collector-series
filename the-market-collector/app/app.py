from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime
from dotenv import load_dotenv
from models import fetch_stocks, store_stocks, stocks_collection

app = Flask(__name__)

# global variable to store fetched stock data
fetched_stocks = []

def fetch_stocks_job():
    global fetched_stocks
    fetched_stocks = fetch_stocks()

def store_stocks_job():
    global fetched_stocks
    store_stocks(fetched_stocks)

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_stocks_job, "interval", minutes=5, next_run_time=datetime.now())
scheduler.add_job(store_stocks_job, "interval", minutes=6, next_run_time=datetime.now())
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
