from pymongo import MongoClient
from datetime import datetime
import requests
import xml.etree.ElementTree as ET

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-scientific-collector"]
papers_collection = db["scientific-collection"]
temp_papers_collection = db["temp-papers-collection"]

def fetch_papers(query="cs"):
    """
    Fetches scientific articles from arXiv using their API.
    """
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=10"
    response = requests.get(url)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        papers = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            paper = {
                "title": entry.find("{http://www.w3.org/2005/Atom}title").text,
                "author": ", ".join([author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")]),
                "publishedAt": entry.find("{http://www.w3.org/2005/Atom}published").text,
                "url": entry.find("{http://www.w3.org/2005/Atom}id").text,
                "abstract": entry.find("{http://www.w3.org/2005/Atom}summary").text,
                "journal": "arXiv"
            }
            papers.append(paper)
        return papers
    else:
        print(f"Failed to fetch articles from arXiv. Status code: {response.status_code}")
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
