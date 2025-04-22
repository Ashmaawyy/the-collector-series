from pymongo import MongoClient
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_fixed
from dotenv import load_dotenv
from pathlib import Path
import requests
import os
import logging

logger = logging.getLogger(__name__)

# Load environment variables first
env_path = Path('.') / 'keys.env'
load_dotenv(env_path)

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['the-scientific-collector']
papers_collection = db['scientific-collection']

# Retry configuration for API calls
@retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
def fetch_papers(days=7, max_results=100):
    """Fetch papers from Springer API with enhanced error handling"""
    papers = []
    SPRINGER_API_KEY = os.getenv('SPRINGER_API_KEY')
    
    if not SPRINGER_API_KEY:
        logger.error("🔑 Missing Springer API key")
        return []

    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        start = 1
        while len(papers) < max_results:
            url = (
                f"https://api.springernature.com/openaccess/json?"
                f"api_key={SPRINGER_API_KEY}&"
                f"q=onlinedatefrom:{start_date} onlinedateto:{end_date}"
            )
            
            response = requests.get(url, headers={
                "User-Agent": "ScientificCollector/1.0",
                "Accept": "application/json"
            }, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"❌ API Error: {response.status_code} - {response.text}")

            data = response.json()
            if not data.get('records'):
                return []

            for record in data['records']:
                paper = {
                    "title": record.get("title", "Untitled"),
                    "doi": record.get("doi", ""),
                    "authors": [c["creator"] for c in record.get("creators", [])],
                    "publisherName": record.get("publisherName", ""),
                    "publicationType": record.get("publicationType", ""),
                    "publicationDate": record.get("publicationDate"),
                    "url": next((u["value"] for u in record.get("url", [])), ""),
                    "abstract": record.get("abstract", ""),
                }
                papers.append(paper)
            
            start += 10

        logger.info(f"✅ API fetched {len(papers)} papers successfully")
        return papers

    except Exception as e:
        logger.error(f"🔥 Critical API Error: {str(e)}")
        return []

def store_papers(papers):
    """Store papers in MongoDB with duplicate checking"""
    try:
        if not papers:
            logger.warning("❌ No found papers to store")
            return

        logger.info("🔍 Checking for Duplicate papers before insertion...")
        new_papers = []

        for paper in papers:
            if papers_collection.find_one({"title": paper["title"], "publicationDate": paper["publicationDate"]}):
                logger.warning(f"⚠️ Found duplicate papers: {paper['title']} - skipping duplicate paper...")
            else:
                new_papers.append(paper)
        
        if new_papers:
            papers_collection.insert_many(new_papers)
            logger.info(f"📚 Inserted {len(new_papers)} new papers")
            return

    except Exception as e:
        logger.error(f"🔥 Insertion Failed due to: {str(e)}")
        return
