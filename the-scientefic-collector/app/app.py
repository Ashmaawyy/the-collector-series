from flask import Flask
from models import fetch_papers, store_papers
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
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

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def fetch_papers_job():
    """Job to fetch papers from Springer API"""
    global papers
    try:
        logger.info("🕸️ Starting paper fetch job")
        papers = fetch_papers()
        logger.info(f"✅ Successfully fetched {len(papers)} papers")
    except Exception as e:
        logger.error(f"🔥 Scheduled job failed: {str(e)}")

def store_papers_job():
    """Job to store papers in MongoDB"""
    global papers
    try:
        if not papers:
            logger.warning("📭 No papers to store")
            return
        else:
            logger.info("📦 Starting paper storage job")
            store_papers(papers)
            logger.info(f"🔄 Stored {len(papers)} papers in MongoDB")
            papers = []

    except Exception as e:
        logger.error(f"🔥 Scheduled job failed: {str(e)}")

# Add scheduled jobs
scheduler.add_job(fetch_papers_job, 'interval', minutes=10, next_run_time=datetime.datetime.now())
scheduler.add_job(store_papers_job, 'interval', minutes=15, next_run_time=datetime.datetime.now()+datetime.timedelta(minutes=1))

#@app.teardown_appcontext
#def shutdown_scheduler(exception=None):
#    """Shut down the scheduler when the app stops"""
#    if scheduler.running:
#        scheduler.shutdown()

# Import routes after app creation to avoid circular imports
from routes import *

if __name__ == "__main__":
    logger.info("🚀 The Scientific Collector starting on port 5000")
    app.run(debug=True, port=5000, host="0.0.0.0")
