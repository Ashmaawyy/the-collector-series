import logging
from pymongo import MongoClient
import requests
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
    api_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        if articles:
            logging.info(f"✅ Successfully fetched {len(articles)} articles from NewsAPI.")
            return articles
        else:
            logging.warning("⚠ No articles found.")
            return []
    else:
        logging.error(f"❌ Failed to fetch articles from NewsAPI. Status code: {response.status_code}")
        return []

def store_articles(articles):
    """
    Stores news articles in MongoDB with the new data structure.
    """
    formatted_articles = []
    
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

    if formatted_articles:
        news_collection.insert_many(formatted_articles)
        logging.info(f"✅ Successfully inserted {len(formatted_articles)} articles into MongoDB.")
    else:
        logging.warning("⚠ No valid and unique articles to insert.")

def get_latest_headlines(limit=50):
    """
    Fetches the latest news articles from MongoDB.
    Returns a list of structured articles sorted by published date.
    """
    latest_articles = list(
        news_collection.find({}, {"_id": 0})
        .sort("publishedAt", -1)
        .limit(limit)
    )
    
    logging.info(f"📢 Retrieved {len(latest_articles)} latest articles from MongoDB.")
    return latest_articles
