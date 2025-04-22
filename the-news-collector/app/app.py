from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from models import fetch_articles, store_articles
from datetime import datetime, timedelta
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="🕒 %(asctime)s - 📍 %(name)s - [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('news_collector.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

fetched_articles = []

def fetch_articles_job():
    global fetched_articles
    logger.info("🕸️ Starting fetch_articles_job...")
    try:
        fetched_articles = fetch_articles()
        logger.info(f"✅ fetch_articles_job completed with {len(fetched_articles)} fresh articles")
    except Exception as e:
        logger.error(f"🔥 fetch_articles_job Failed: {str(e)}")

def store_articles_job():
    global fetched_articles
    logger.info("💾 Starting store_articles_job")
    try:
        store_articles(fetched_articles)
        logger.info(f"📦 store_articles_job executed successfully storing {len(fetched_articles)} fresh articles")
        fetched_articles = []
        logger.info("🔄 Article Cache Reset")
    except Exception as e:
        logger.error(f"🔥 store_articles_job Failed: {str(e)}")

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_articles_job, "interval", minutes=3, next_run_time=datetime.now())
scheduler.add_job(store_articles_job, "interval", minutes=4, next_run_time=datetime.now() + timedelta(minutes=1))

# Import routes
from routes import *

if __name__ == "__main__":
    logger.info("🚀 The News Collector is starting on port 5000")

     # Prevent scheduler from starting twice
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":  
        scheduler.start()

    app.run(debug=True, port=5000, host="0.0.0.0")
