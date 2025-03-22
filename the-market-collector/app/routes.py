from flask import render_template, request, jsonify
from app import app
from models import stocks_collection
import logging

logger = logging.getLogger(__name__)
PAGE_SIZE = 15  # Number of items per load

@app.route("/")
def home():
    """Main endpoint with paginated stocks"""
    return render_template("index.html")

@app.route('/api/load-more-stocks')
def load_more_stocks():
    """API endpoint for infinite scroll loading"""
    try:
        page = int(request.args.get("page", 1))
        query = request.args.get("q", "").strip().upper()
        
        skip = (page - 1) * PAGE_SIZE
        
        pipeline = [
            {"$match": {"symbol": {"$regex": f".*{query}.*", "$options": "i"}}},
            {"$sort": {"timestamp": -1}},
            {"$skip": skip},
            {"$limit": PAGE_SIZE},
            {"$project": {
                "_id": 0,
                "symbol": 1,
                "timestamp": 1,
                "open": 1,
                "high": 1,
                "low": 1,
                "close": 1,
                "volume": 1
            }}
        ]
        
        stocks = list(stocks_collection.aggregate(pipeline))
        
        # Check if there are more stocks to load
        next_page = page + 1 if len(stocks) == PAGE_SIZE else None
        
        return jsonify({"stocks": stocks, "next_page": next_page})
    
    except Exception as e:
        logger.error(f"🔥 Load more error: {str(e)}")
        return jsonify({"error": "Failed to load more stocks"}), 500
