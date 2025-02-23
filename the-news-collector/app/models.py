from pymongo import MongoClient
from datetime import datetime
import requests
import feedparser

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-news-collector"]
articles_collection = db["news-collection"]
temp_articles_collection = db["temp-news-collection"]

def fetch_articles(query="news"):
    """
    Fetches news articles from Medium using RSS feeds.
    """
    url = f"https://medium.com/feed/tag/{query}"
    response = requests.get(url)
    
    if response.status_code == 200:
        feed = feedparser.parse(response.content)
        articles = []
        for entry in feed.entries:
            articles.append({
                "headline": entry.title,
                "summary": entry.summary if "summary" in entry else "N/A",
                "publishedAt": entry.published if "published" in entry else datetime.utcnow().isoformat(),
                "url": entry.link,
                "author": entry.author if "author" in entry else "N/A",
                "category": "Medium"
            })
        return articles
    else:
        print(f"Failed to fetch articles from Medium. Status code: {response.status_code}")
        return []

def store_articles(articles):
    """
    Stores news articles in MongoDB with the new data structure.
    """
    formatted_articles = []

    for article in articles:
        if not articles_collection.find_one({"headline": article["headline"]}):
            formatted_articles.append(article)

    if formatted_articles:
        articles_collection.insert_many(formatted_articles)
        print(f"✅ Successfully inserted {len(formatted_articles)} articles into MongoDB.")
    else:
        print(f"⚠ No valid articles to insert.")

def fetch_and_store_temp_articles():
    """
    Fetches articles and stores them in a temporary collection.
    """
    articles = fetch_articles()
    if articles:
        temp_articles_collection.insert_many(articles)
        print(f"✅ Successfully fetched and stored {len(articles)} articles in the temporary collection.")

def store_temp_articles():
    """
    Stores articles from the temporary collection into the main collection.
    """
    temp_articles = list(temp_articles_collection.find())
    unique_articles = [article for article in temp_articles if not articles_collection.find_one({"headline": article["headline"]})]
    
    if unique_articles:
        articles_collection.insert_many(unique_articles)
        print(f"✅ Successfully moved {len(unique_articles)} unique articles from the temporary collection to the main collection.")
    else:
        print(f"⚠ No unique articles to move.")

    temp_articles_collection.delete_many({})
    print(f"✅ Cleared the temporary collection.")

def get_latest_headlines(limit=50):
    """
    Fetches the latest news articles from MongoDB.
    Returns a list of structured articles sorted by published date.
    """
    latest_articles = list(
        articles_collection.find({}, {"_id": 0})  # Exclude MongoDB _id field
        .sort("publishedAt", -1)  # Sort by latest published date
        .limit(limit)  # Limit results
    )

    return latest_articles
