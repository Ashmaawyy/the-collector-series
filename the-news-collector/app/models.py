from pymongo import MongoClient
from datetime import datetime

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-news-collector"]
articles_collection = db["news-articles"]

def store_articles(articles):
    """
    Stores news articles in MongoDB with the new data structure.
    """
    formatted_articles = []

    for article in articles:
        data = {
            "headline": article.get("headline", "N/A"),
            "summary": article.get("summary", "N/A"),
            "publishedAt": article.get("publishedAt", datetime.utcnow()),  # Default to now if missing
            "url": article.get("url", "N/A"),
            "author": article.get("author", "N/A"),
            "category": article.get("category", "N/A")
        }
        formatted_articles.append(data)

    if formatted_articles:
        articles_collection.insert_many(formatted_articles)
        print(f"✅ Successfully inserted {len(formatted_articles)} articles into MongoDB.")
    else:
        print(f"⚠ No valid articles to insert.")

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
