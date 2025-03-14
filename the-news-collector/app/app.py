from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
from models import fetch_articles, store_articles, news_collection
from datetime import datetime
import logging
import re

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
scheduler.add_job(fetch_articles_job, "interval", minutes=5, next_run_time=datetime.now())
scheduler.add_job(store_articles_job, "interval", minutes=6, next_run_time=datetime.now())
scheduler.start()

@app.route('/')
def index():
    logger.info("🌐 Home page accessed")
    page = request.args.get("page", 1, type=int)
    per_page = 5
    total_count = news_collection.count_documents({})
    total_pages = (total_count + per_page - 1) // per_page
    
    news = list(news_collection.find().sort("publishedAt", -1).skip((page - 1) * per_page).limit(per_page))
    
    return render_template("index.html", news=news, page=page, total_pages=total_pages)

@app.route('/update_news', methods=['GET'])
def update_news():
    logger.info("🔄 Manual news update triggered")
    try:
        articles = fetch_articles()
        store_articles(articles)
        return jsonify({"status": "success", "message": "News updated!"})
    except Exception as e:
        logger.error(f"❌ Manual update failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/load_latest_news')
def load_latest_news():
    logger.debug("📥 Loading latest news")
    latest_news = list(news_collection.find().sort("publishedAt", -1).limit(5))

    news_data = [
        {
            "title": item["title"],
            "source": item["source"],
            "author": item.get("author", "N/A"),
            "publishedAt": item["publishedAt"] if isinstance(item["publishedAt"], str) else item["publishedAt"].strftime("%Y-%m-%d %H:%M:%S"),
            "url": item["url"],
            "urlToImage": item.get("urlToImage", "")
        } for item in latest_news
    ]

    return jsonify({"news": news_data})

@app.route('/load_more_news')
def load_more_news():
    page = request.args.get("page", 1, type=int)
    logger.info(f"📖 Loading more news (page {page})")
    per_page = 10

    news = list(news_collection.find().sort("publishedAt", -1).skip((page - 1) * per_page).limit(per_page))

    news_data = [
        {
            "title": item["title"],
            "source": item["source"],
            "author": item.get("author", "N/A"),
            "publishedAt": item["publishedAt"] if isinstance(item["publishedAt"], str) else item["publishedAt"].strftime("%Y-%m-%d %H:%M:%S"),
            "url": item["url"],
            "urlToImage": item.get("urlToImage", "")
        } for item in news
    ]

    return jsonify({"news": news_data, "page": page})

@app.route('/search_news')
def search_news():
    query = re.escape(request.args.get("q", "").strip().lower())
    logger.info(f"🔍 Searching for: '{query}'")
    try:
        news_collection.create_index([("title", "text")])
        news = list(news_collection.find({"$text": {"$search": query}}).limit(10))
        
        logger.info(f"🔎 Found {len(news)} results for '{query}'")
        news_data = [
            {
                "title": item["title"],
                "source": item["source"],
                "author": item.get("author", "N/A"),
                "publishedAt": item.get("publishedAt", ""),
                "url": item["url"],
                "urlToImage": item.get("urlToImage", "")
            } for item in news
        ]
        return jsonify({"news": news_data})
    except Exception as e:
        logger.error(f"❌ Search failed: {str(e)}")
        return jsonify({"news": []})

if __name__ == "__main__":
    logger.info("🚀 The News Collector is starting on port 5000")
    app.run(debug=True, port=5000, host="0.0.0.0")
