from pymongo import MongoClient
from datetime import datetime, timedelta
import requests
import os
import logging
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

# Retry configuration for API calls
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_papers(days=60, max_results=100):
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
                f"q=onlinedate:{start_date} TO {end_date}&"
                f"p={start}&s=10"
            )
            
            response = requests.get(url, headers={
                "User-Agent": "ScientificCollector/1.0",
                "Accept": "application/json"
            }, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"❌ API Error: {response.status_code} - {response.text}")
                break

            data = response.json()
            if not data.get('records'):
                break

            for record in data['records']:
                paper = {
                    "title": record.get("title", "Untitled"),
                    "doi": record.get("doi", ""),
                    "authors": [c["creator"] for c in record.get("creators", [])],
                    "publication_date": record.get("publicationDate"),
                    "url": next((u["value"] for u in record.get("url", []) if u["format"] == "html"), ""),
                    "abstract": record.get("abstract", ""),
                    "journal": record.get("publicationName", "Springer"),
                    "subjects": [s["name"] for s in record.get("subjects", [])]
                }
                papers.append(paper)
            
            start += 10

        logger.info(f"✅ Fetched {len(papers)} papers")
        return papers

    except Exception as e:
        logger.error(f"🔥 Critical API error: {str(e)}")
        return []

def store_papers(papers):
    """Store papers in MongoDB with duplicate checking"""
    try:
        if not papers:
            logger.warning("📭 No papers to store")
            return

        operations = [
            {
                'update_one': {
                    'filter': {'doi': paper['doi']},
                    'update': {'$setOnInsert': paper},
                    'upsert': True
                }
            } for paper in papers if paper.get('doi')
        ]

        if operations:
            result = papers.bulk_write(operations)
            logger.info(
                f"📚 Storage: {result.upserted_count} new, "
                f"{len(papers) - result.upserted_count} duplicates"
            )
            
    except Exception as e:
        logger.error(f"🔥 Storage failed: {str(e)}")
