from pymongo import MongoClient
from datetime import datetime
from scholarly import scholarly

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-scientefic-collector"]
papers_collection = db["scientefic-papers"]

def fetch_papers(query="scientific papers"):
    """
    Fetches scientific papers using the scholarly library.
    """
    search_query = scholarly.search_pubs(query)
    papers = []
    for paper in search_query:
        paper_data = scholarly.fill(paper)
        papers.append({
            "title": paper_data["bib"]["title"],
            "author": paper_data["bib"].get("author", "N/A"),
            "publishedAt": paper_data["bib"].get("pub_year", datetime.utcnow().year),
            "url": paper_data.get("eprint_url", ""),
            "abstract": paper_data["bib"].get("abstract", ""),
            "journal": paper_data["bib"].get("journal", "N/A")
        })
    return papers

def store_papers(papers):
    """
    Stores scraped scientific papers in MongoDB with the new data structure.
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
