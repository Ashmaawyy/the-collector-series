from flask import render_template, request, jsonify
from app import app
from models import papers_collection
import logging

logger = logging.getLogger(__name__)
DEFAULT_PER_PAGE = 8

@app.route('/')
def home():
    """Main endpoint with paginated papers"""
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = int(request.args.get("per_page", DEFAULT_PER_PAGE))
        
        # Get papers with proper MongoDB query
        papers = list(papers_collection.find()
            .sort("publicationDate", -1)
            .skip((page - 1) * per_page)
            .limit(per_page)
        )

        # Convert MongoDB objects to dicts and remove duplicates
        seen_dois = set()
        paper_data = []
        for p in papers:
            title = p.get("title", "")
            if title and title not in seen_dois:
                seen_dois.add(title)
                paper_data.append({
                    "title": p.get(title, "Untitled"),
                    "doi": p.get("doi", ""),
                    "authors": p.get("authors", ["Unknown Author"]),
                    "journal": p.get("publisherName", "Unknown Journal"),
                    "publicationDate": p.get("publicationDate", "Unknown Date"),
                    "abstract": p.get("abstract", "No abstract available"),
                    "url": p.get("url", "#")
                })

        return render_template("index.html", papers=paper_data, page=page)
    
    except Exception as e:
        logger.error(f"Route error: {str(e)}")
        return render_template("error.html"), 500

@app.route('/api/papers')
def get_papers():
    """API endpoint for papers"""
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(int(request.args.get("per_page", DEFAULT_PER_PAGE)), 100)
        query = request.args.get("q", "")
        
        pipeline = [
            {"$match": {"$text": {"$search": query}}} if query else {"$match": {}},
            {"$sort": {"publicationDate": -1}},
            {"$skip": (page - 1) * per_page},
            {"$limit": per_page},
            {"$project": {"_id": 0}}
        ]
        
        papers = list(papers_collection.aggregate(pipeline))
        return jsonify({"papers": papers, "page": page})
    
    except Exception as e:
        logger.error(f"🔥 API error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        papers_collection.find_one()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logger.error(f"🔴 Health check failed: {str(e)}")
        return jsonify({"status": "unhealthy"}), 500

@app.route('/api/load-more-papers')
def load_more_papers():
    """API endpoint for infinite scroll loading"""
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = 8
        query = request.args.get("q", "").strip()
        
        pipeline = [
            {"$sort": {"publicationDate": -1}},
            {"$skip": (page - 1) * per_page},
            {"$limit": per_page},
            {"$project": {
                "_id": 0,
                "title": 1,
                "doi": 1,
                "authors": 1,
                "publisherName": 1,
                "publicationType": 1,
                "publicationDate": 1,
                "url": 1,
                "abstract": 1
            }}
        ]
        
        if query:
            pipeline.insert(0, {"$match": {"$text": {"$search": query}}})
            
        papers = list(papers_collection.aggregate(pipeline))
        
        next_page = page + 1 if len(papers) == per_page else None
        
        return jsonify({
            "papers": papers,
            "next_page": next_page
        })
        
    except Exception as e:
        logger.error(f"Load more error: {str(e)}")
        return jsonify({"error": "Failed to load papers"}), 500
