import logging
from pymongo import MongoClient
import requests
import os
from dotenv import load_dotenv

# Configure logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('keys.env')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-news-collector"]
news_collection = db["news-collection"]

def fetch_articles():
    """
    Fetches news articles from NewsAPI.
    """
    logger.info("📡 Connecting to NewsAPI")
    try:
        api_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            if articles:
                logger.info(f"✅ Fetched {len(articles)} articles from NewsAPI")
                return articles
            else:
                logger.warning("📭 No articles found in response")
                return []
        else:
            logger.error(f"❌ NewsAPI request failed (HTTP {response.status_code})")
            return []
    except Exception as e:
        logger.error(f"🔥 Critical API error: {str(e)}")
        return []

def store_articles(articles):
    """
    Stores news articles in MongoDB with the new data structure.
    """
    try:
        formatted_articles = []
        duplicates = 0

        logger.info("🧹 Processing articles for storage")
        for article in articles:
            if not news_collection.find_one({"title": article["title"], "publishedAt": article["publishedAt"]}):
                formatted_articles.append({
                    "title": article["title"],
                    "source": article["source"]["name"],
                    "author": article.get("author", "N/A"),
                    "publishedAt": article["publishedAt"],
                    "url": article["url"],
                    "urlToImage": article.get("urlToImage", ""),
                    "category": "General"
                })
            else:
                duplicates += 1

        if duplicates > 0:
            logger.warning(f"⚠️ Found {duplicates} duplicate articles")

        if formatted_articles:
            news_collection.insert_many(formatted_articles)
            logger.info(f"📚 Stored {len(formatted_articles)} new articles")
        else:
            logger.warning("📭 No new articles to store")
            Exception("❌ No unique articles to store")
            
    except Exception as e:
        logger.error(f"🔥 Storage failed: {str(e)}")

def get_latest_headlines(limit=50):
    """
    Fetches the latest news articles from MongoDB.
    """
    logger.info(f"📰 Retrieving latest {limit} headlines")
    try:
        latest_articles = list(
            news_collection.find({}, {"_id": 0})
            .sort("publishedAt", -1)
            .limit(limit)
        )
        logger.debug(f"📨 Delivered {len(latest_articles)} articles")
        return latest_articles
    except Exception as e:
        logger.error(f"❌ Failed to retrieve headlines: {str(e)}")
        return []
