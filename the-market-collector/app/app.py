from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from models import fetch_stocks, store_stocks
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="🕒 %(asctime)s - 📍 %(name)s - [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('market_collector.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
from routes import *

fetched_stocks = []

def fetch_stocks_job():
    global fetched_stocks
    logger.info("🔄 Starting scheduled stock data fetch...")
    fetched_stocks = fetch_stocks()

def store_stocks_job():
    global fetched_stocks
    logger.info("💽 Starting scheduled stock data storage...")
    store_stocks(fetched_stocks)

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_stocks_job, "interval", minutes=5, next_run_time=datetime.now())
scheduler.add_job(store_stocks_job, "interval", minutes=6, next_run_time=datetime.now()+timedelta(minutes=1))

if __name__ == "__main__":
    logger.info("🚀 The Market Collector starting on port 5000")

     # Prevent scheduler from starting twice
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":  
        scheduler.start()

    app.run(debug=True, port=5000, host="0.0.0.0")
