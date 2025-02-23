from pymongo import MongoClient
from datetime import datetime
import requests
import feedparser
import os
from dotenv import load_dotenv

# Load environment variables from keys.env
load_dotenv('keys.env')

# Get the API key from the environment variable
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-news-collector"]
news_collection = db["news-collection"]
temp_news_collection = db["temp-news-collection"]

def fetch_articles():
    """
    Fetches news articles from NewsAPI.
    """
    api_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return articles
    else:
        print(f"Failed to fetch articles from NewsAPI. Status code: {response.status_code}")
        return []

def store_articles(articles):
    """
    Stores news articles in MongoDB with the new data structure.
    """
    formatted_articles = []

    for article in articles:
        if not news_collection.find_one({"title": article["title"]}):
            formatted_articles.append({
                "title": article["title"],
                "source": article["source"]["name"],
                "author": article.get("author", "N/A"),
                "publishedAt": article.get("publishedAt", datetime.utcnow()),
                "url": article["url"],
                "urlToImage": article.get("urlToImage", ""),
                "category": "General"
            })

    if formatted_articles:
        news_collection.insert_many(formatted_articles)
        print(f"✅ Successfully inserted {len(formatted_articles)} articles into MongoDB.")
    else:
        print(f"⚠ No valid articles to insert.")

def fetch_and_store_temp_articles():
    """
    Fetches articles and stores them in a temporary collection.
    """
    articles = fetch_articles()
    if articles:
        temp_news_collection.insert_many(articles)
        print(f"✅ Successfully fetched and stored {len(articles)} articles in the temporary collection.")

def store_temp_articles():
    """
    Stores articles from the temporary collection into the main collection.
    """
    temp_articles = list(temp_news_collection.find())
    unique_articles = [article for article in temp_articles if not news_collection.find_one({"title": article["title"]})]
    
    if unique_articles:
        news_collection.insert_many(unique_articles)
        print(f"✅ Successfully moved {len(unique_articles)} unique articles from the temporary collection to the main collection.")
    else:
        print(f"⚠ No unique articles to move.")

    temp_news_collection.delete_many({})
    print(f"✅ Cleared the temporary collection.")

def get_latest_headlines(limit=50):
    """
    Fetches the latest news articles from MongoDB.
    Returns a list of structured articles sorted by published date.
    """
    latest_articles = list(
        news_collection.find({}, {"_id": 0})  # Exclude MongoDB _id field
        .sort("publishedAt", -1)  # Sort by latest published date
        .limit(limit)  # Limit results
    )

    return latest_articles
