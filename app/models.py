from config import COLLECTION_NAME
from app import db
from datetime import datetime

news_collection = db[COLLECTION_NAME]

def store_headlines(source, headlines):
    """Stores scraped headlines in MongoDB"""
    data = {
        "source": source,
        "headlines": headlines,
        "scraped_at": datetime.utcnow()
    }
    news_collection.insert_one(data)

def get_latest_headlines():
    """Fetches the latest headlines from MongoDB"""
    return list(news_collection.find().sort("scraped_at", -1).limit(5))
