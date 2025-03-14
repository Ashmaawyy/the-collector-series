from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from models import fetch_papers, store_papers, papers_collection
from pymongo import MongoClient
import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="🕒 %(asctime)s - 📍 %(name)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scientefic_collector.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Global variable to store fetched papers
fetched_papers = []

def fetch_papers_job():
    global fetched_papers
    logger.info("🕸️ Starting paper fetch job")
    try:
        fetched_papers = fetch_papers()
        logger.info(f"✅ Fetched {len(fetched_papers)} papers")
    except Exception as e:
        logger.error(f"🔥 Failed to fetch papers: {str(e)}")

def store_papers_job():
    global fetched_papers
    logger.info("💾 Starting paper storage job")
    try:
        store_papers(fetched_papers)
        logger.info("🔄 Reset fetched papers cache")
        fetched_papers = []
    except Exception as e:
        logger.error(f"🔥 Failed to store papers: {str(e)}")

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_papers_job, "interval", minutes=5, next_run_time=datetime.datetime.now())
scheduler.add_job(store_papers_job, "interval", minutes=6, next_run_time=datetime.datetime.now())
scheduler.start()

@app.route('/')
def index():
    logger.info("🌐 Home page accessed")
    page = request.args.get("page", 1, type=int)
    per_page = 5
    total_count = papers_collection.count_documents({})
    total_pages = (total_count + per_page - 1) // per_page
    
    papers = list(papers_collection.find().sort("publishedAt", -1).skip((page - 1) * per_page).limit(per_page))
    
    return render_template("index.html", papers=papers, page=page, total_pages=total_pages)

@app.route('/update_papers', methods=['GET'])
def update_papers():
    logger.info("🔄 Manual paper update triggered")
    try:
        fetch_papers_job()
        store_papers_job()
        return jsonify({"status": "success", "message": "Papers updated!"})
    except Exception as e:
        logger.error(f"🔥 Manual update failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/load_latest_papers')
def load_latest_papers():
    logger.debug("📥 Loading latest papers")
    latest_papers = list(papers_collection.find().sort("publishedAt", -1).limit(5))

    papers_data = [
        {
            "title": item["title"],
            "author": item.get("author", "N/A"),
            "publishedAt": item["publishedAt"],
            "url": item["url"],
            "abstract": item.get("abstract", ""),
            "journal": item.get("journal", "N/A")
        } for item in latest_papers
    ]

    return jsonify({"papers": papers_data})

@app.route('/load_more_papers')
def load_more_papers():
    page = request.args.get("page", 1, type=int)
    logger.info(f"📖 Loading more papers (page {page})")
    per_page = 10

    papers = list(papers_collection.find().sort("publishedAt", -1).skip((page - 1) * per_page).limit(per_page))

    papers_data = [
        {
            "title": item["title"],
            "author": item.get("author", "N/A"),
            "publishedAt": item["publishedAt"],
            "url": item["url"],
            "abstract": item.get("abstract", ""),
            "journal": item.get("journal", "N/A")
        } for item in papers
    ]

    return jsonify({"papers": papers_data, "page": page})

@app.route('/search_papers')
def search_papers():
    query = request.args.get("q", "").lower()
    logger.info(f"🔍 Searching papers for: {query}")
    papers = list(papers_collection.find({"title": {"$regex": query, "$options": "i"}}).limit(10))

    papers_data = [
        {
            "title": item["title"],
            "author": item.get("author", "N/A"),
            "publishedAt": item.get("publishedAt", ""),
            "url": item["url"],
            "abstract": item.get("abstract", ""),
            "journal": item.get("journal", "N/A")
        } for item in papers
    ]

    return jsonify({"papers": papers_data})

if __name__ == "__main__":
    logger.info("🚀 The Scientefic Collector is starting on port 5000")
    app.run(debug=True, port=5000, host="0.0.0.0")
