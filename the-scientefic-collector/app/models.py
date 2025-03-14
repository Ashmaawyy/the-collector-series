from pymongo import MongoClient
from datetime import datetime, timedelta
import requests
import os
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from keys.env
load_dotenv('C:/Users/ALDEYAA/OneDrive - AL DEYAA MEDIA PRODUCTION/Documents/the-collector-series/keys.env')

# Get the API key from the environment variable
SPRINGER_API_KEY = os.getenv('SPRINGER_API_KEY')

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-scientific-collector"]
papers_collection = db["scientific-collection"]

def fetch_papers(days=60, max_results=100):
    """
    Fetches newly published scientific articles from Springer using their API.
    """
    papers = []
    start = 1
    rows = 10  # Number of results per page (adjust as needed)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    try:
        while len(papers) < max_results:
            url = f"https://api.springernature.com/openaccess/json?api_key={SPRINGER_API_KEY}&q=onlinedate:{start_date.strftime('%Y-%m-%d')} TO {end_date.strftime('%Y-%m-%d')}&p={start}&s={rows}"
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if not data['records']:
                    logger.info("📭 No more records to fetch")
                    break  # No more records to fetch

                for record in data['records']:
                    paper = {
                        "title": record.get("title", "No title"),
                        "author": ", ".join([author["creator"] for author in record.get("creators", [])]),
                        "publishedAt": record.get("publicationDate", "No date"),
                        "url": record.get("url", [{"value": "No URL"}])[0]["value"],
                        "abstract": {
                            "h1": "Abstract",
                            "p": record.get("abstract", "No abstract")
                        },
                        "journal": record.get("publicationName", "Springer")
                    }
                    papers.append(paper)
                    if len(papers) >= max_results:
                        break

                start += rows
                logger.debug(f"📥 Fetched {len(papers)} papers so far")
            else:
                logger.error(f"❌ Failed to fetch articles from Springer. Status code: {response.status_code}")
                break

        logger.info(f"✅ Successfully fetched {len(papers)} papers from Springer")
        return papers
    
    except Exception as e:
        logger.error(f"🔥 Critical error fetching papers: {str(e)}")
        return []

def store_papers(papers):
    """
    Stores scraped scientific articles in MongoDB with the new data structure.
    """
    try:
        formatted_papers = []
        duplicates = 0

        for paper in papers:
            if not papers_collection.find_one({"title": paper["title"]}):
                formatted_papers.append(paper)
            else:
                duplicates += 1

        if duplicates > 0:
            logger.warning(f"⚠️ Found {duplicates} duplicate papers")

        if formatted_papers:
            papers_collection.insert_many(formatted_papers)
            logger.info(f"📚 Successfully inserted {len(formatted_papers)} papers into MongoDB")
        else:
            logger.warning("📭 No valid and unique papers to insert")
    
    except Exception as e:
        logger.error(f"🔥 Failed to store papers: {str(e)}")
