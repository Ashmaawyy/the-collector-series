from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from models import fetch_articles, store_articles
from datetime import datetime, timedelta
import logging

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
    logger.info("🕸️ Starting news collection job")
    try:
        fetched_articles = fetch_articles()
        logger.info(f"✅ Collected {len(fetched_articles)} fresh articles")
    except Exception as e:
        logger.error(f"🔥 Failed to collect articles: {str(e)}")

def store_articles_job():
    global fetched_articles
    logger.info("💾 Starting article storage job")
    try:
        store_articles(fetched_articles)
        fetched_articles = []
        logger.info("🔄 Reset article cache")
    except Exception as e:
        logger.error(f"🔥 Failed to store articles: {str(e)}")

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_articles_job, "interval", minutes=3, next_run_time=datetime.now())
scheduler.add_job(store_articles_job, "interval", minutes=4, next_run_time=datetime.now() + timedelta(minutes=1))
scheduler.start()

# Import routes
from routes import *

if __name__ == "__main__":
    logger.info("🚀 The News Collector is starting on port 5000")
    app.run(debug=True, port=5000, host="0.0.0.0")
