from flask import Flask
from models import fetch_papers, store_papers
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
import logging

papers = []

# Configure logging before creating app instance
logging.basicConfig(
    level=logging.INFO,
    format="🕒 %(asctime)s - 📍 %(name)s - [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scientific_collector.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

def fetch_papers_job():
    """Job to fetch papers from Springer API"""
    global papers
    try:
        logger.info("🕸️  Starting paper fetch job")
        papers = fetch_papers()
        if not papers:
            logger.warning("📭 No papers fetched")
        else:
            logger.info(f"✅ SUCCESSFULL: fetch_papers_job Completed Successfully")
    except Exception as e:
        logger.error(f"🔥 FAILURE: fetch_papers_job failed due to: {str(e)}")

def store_papers_job():
    """Job to store papers in MongoDB"""
    global papers
    try:
        logger.info("📦 Starting store_papers_job...")
        store_papers(papers)
        logger.info(f"✅ SUCCESSFULL: store_papers_job Completed Successfully")
        papers = []
        logger.info("🔄 Papers Cache Reset")

    except Exception as e:
        logger.error(f"🔥 FAILURE: store_papers_job failed due to: {str(e)}")
        return

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_papers_job, 'interval', minutes=5, next_run_time=datetime.now())
scheduler.add_job(store_papers_job, 'interval', minutes=6, next_run_time=datetime.now()+timedelta(minutes=1))

# Import routes after app creation to avoid circular imports
from routes import *

if __name__ == "__main__":
    logger.info("🚀 The Scientific Collector starting on port 5000")

     # Prevent scheduler from starting twice
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":  
        scheduler.start()
    
    app.run(debug=True, port=5000, host="0.0.0.0")
