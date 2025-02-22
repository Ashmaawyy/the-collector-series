from pymongo import MongoClient
from datetime import datetime

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-scientefic-collector"]
papers_collection = db["scientefic-papers"]

def store_papers(papers):
    """
    Stores scraped scientific papers in MongoDB with the new data structure.
    """
    formatted_papers = []

    for paper in papers:
        data = {
            "title": paper.get("title", "N/A"),
            "author": paper.get("author", "N/A"),
            "publishedAt": paper.get("publishedAt", datetime.utcnow()),  # Default to now if missing
            "url": paper.get("url", "N/A"),
            "abstract": paper.get("abstract", "N/A"),
            "journal": paper.get("journal", "N/A"),
            "category": paper.get("category", "N/A")
        }
        formatted_papers.append(data)

    if formatted_papers:
        papers_collection.insert_many(formatted_papers)
        print(f"✅ Successfully inserted {len(formatted_papers)} papers into MongoDB.")
    else:
        print(f"⚠ No valid papers to insert.")

def get_latest_papers(limit=50):
    """
    Fetches the latest scientific papers from MongoDB.
    Returns a list of structured papers sorted by published date.
    """
    latest_papers = list(
        papers_collection.find({}, {"_id": 0})  # Exclude MongoDB _id field
        .sort("publishedAt", -1)  # Sort by latest published date
        .limit(limit)  # Limit results
    )

    return latest_papers
