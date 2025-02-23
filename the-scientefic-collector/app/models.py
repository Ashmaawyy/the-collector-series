from pymongo import MongoClient
from datetime import datetime
import requests
import feedparser

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-scientific-collector"]
papers_collection = db["scientific-collection"]
temp_papers_collection = db["temp-papers-collection"]

def fetch_papers(query="science"):
    """
    Fetches scientific articles from Medium using RSS feeds.
    """
    url = f"https://medium.com/feed/tag/{query}"
    response = requests.get(url)
    
    if response.status_code == 200:
        feed = feedparser.parse(response.content)
        papers = []
        for entry in feed.entries:
            papers.append({
                "title": entry.title,
                "author": entry.author if "author" in entry else "N/A",
                "publishedAt": entry.published if "published" in entry else datetime.utcnow().isoformat(),
                "url": entry.link,
                "abstract": entry.summary if "summary" in entry else "N/A",
                "journal": "Medium"
            })
        return papers
    else:
        print(f"Failed to fetch articles from Medium. Status code: {response.status_code}")
        return []

def store_papers(papers):
    """
    Stores scraped scientific articles in MongoDB with the new data structure.
    """
    formatted_papers = []

    for paper in papers:
        if not papers_collection.find_one({"title": paper["title"]}):
            formatted_papers.append(paper)

    if formatted_papers:
        papers_collection.insert_many(formatted_papers)
        print(f"✅ Successfully inserted {len(formatted_papers)} papers into MongoDB.")
    else:
        print(f"⚠ No valid papers to insert.")

def fetch_and_store_temp_papers():
    """
    Fetches papers and stores them in a temporary collection.
    """
    papers = fetch_papers()
    if papers:
        temp_papers_collection.insert_many(papers)
        print(f"✅ Successfully fetched and stored {len(papers)} papers in the temporary collection.")

def store_temp_papers():
    """
    Stores papers from the temporary collection into the main collection.
    """
    temp_papers = list(temp_papers_collection.find())
    store_papers(temp_papers)
    temp_papers_collection.delete_many({})
    print(f"✅ Successfully moved {len(temp_papers)} papers from the temporary collection to the main collection.")
