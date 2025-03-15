from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import datetime
import logging

# Load environment variables first
env_path = Path('.') / 'keys.env'
load_dotenv(env_path)

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

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["the-scientific-collector"]
papers_collection = db["scientific-collection"]

# Initialize scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

def fetch_papers_job():
    """Job to fetch papers from Springer API"""
    from models import fetch_papers, store_papers
    try:
        logger.info("🕸️ Starting paper fetch job")
        papers = fetch_papers()
        store_papers(papers)
        logger.info(f"✅ Successfully processed {len(papers)} papers")
    except Exception as e:
        logger.error(f"🔥 Scheduled job failed: {str(e)}")

# Add scheduled jobs
scheduler.add_job(
    fetch_papers_job,
    'interval',
    minutes=15,
    next_run_time=datetime.datetime.now()
)

@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    """Shut down the scheduler when the app stops"""
    if scheduler.running:
        scheduler.shutdown()

# Import routes after app creation to avoid circular imports
from routes import *

if __name__ == "__main__":
    logger.info("🚀 The Scientific Collector starting on port 5000")
    app.run(debug=False, port=5000, host="0.0.0.0")
