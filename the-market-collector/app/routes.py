from flask import render_template, request, jsonify
from app import app
from models import stocks_collection

PAGE_SIZE = 6  # Number of items per load

@app.route("/")
def home():
    """Main route serving the initial dashboard view"""
    return render_template("index.html")

@app.route('/load_more_stocks')
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
        
        return jsonify({"stocks": stocks})
    
    except Exception as e:
        app.logger.error(f"🔥 Load more error: {str(e)}")
        return jsonify({"error": "Failed to load more stocks"}), 500
