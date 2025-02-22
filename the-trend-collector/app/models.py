from config import COLLECTION_NAME
from app import db
from datetime import datetime

trends_collection = db[COLLECTION_NAME]

def store_trends(source, trends):
    """
    Stores scraped social media trends in MongoDB with the new data structure.
    """
    formatted_trends = []

    for trend in trends:
        data = {
            "name": trend.get("name", "N/A"),
            "url": trend.get("url", "N/A"),
            "tweet_volume": trend.get("tweet_volume", "N/A"),
            "timestamp": trend.get("timestamp", datetime.utcnow()),  # Default to now if missing
            "source": source  # Source of the trend (e.g., Twitter, Reddit, YouTube)
        }
        formatted_trends.append(data)

    if formatted_trends:
        trends_collection.insert_many(formatted_trends)
        print(f"✅ Successfully inserted {len(formatted_trends)} trends from {source} into MongoDB.")
    else:
        print(f"⚠ No valid trends to insert for {source}.")

def get_latest_trends(limit=50):
    """
    Fetches the latest social media trends from MongoDB.
    Returns a list of structured trends sorted by timestamp.
    """
    latest_trends = list(
        trends_collection.find({}, {"_id": 0})  # Exclude MongoDB _id field
        .sort("timestamp", -1)  # Sort by latest timestamp
        .limit(limit)  # Limit results
    )

    return latest_trends
