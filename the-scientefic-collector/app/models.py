from pymongo import MongoClient
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables from keys.env
load_dotenv('C:/Users/ALDEYAA/OneDrive - AL DEYAA MEDIA PRODUCTION/Documents/the-collector-series/keys.env')

# Get the API key from the environment variable
SPRINGER_API_KEY = os.getenv('SPRINGER_API_KEY')

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-scientific-collector"]
papers_collection = db["scientific-collection"]
temp_papers_collection = db["temp-papers-collection"]

def fetch_papers():
    """
    Fetches scientific articles from Springer using their API.
    """
    url = f"https://api.springernature.com/openaccess/json?api_key={SPRINGER_API_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        papers = []
        for record in data['records']:
            paper = {
                "title": record.get("title", "No title"),
                "author": ", ".join([author["creator"] for author in record.get("creators", [])]),
                "publishedAt": record.get("publicationDate", "No date"),
                "url": record.get("url", [{"value": "No URL"}])[0]["value"],
                "abstract": record.get("abstract", "No abstract"),
                "journal": record.get("publicationName", "Springer")
            }
            papers.append(paper)
        return papers
    else:
        print(f"❌️ Failed to fetch articles from Springer. Status code: {response.status_code}")
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
    unique_papers = [paper for paper in temp_papers if not papers_collection.find_one({"title": paper["title"]})]
    
    if unique_papers:
        papers_collection.insert_many(unique_papers)
        print(f"✅ Successfully moved {len(unique_papers)} unique papers from the temporary collection to the main collection.")
    else:
        print(f"⚠ No unique papers to move.")

    temp_papers_collection.delete_many({})
    print(f"✅ Cleared the temporary collection.")
