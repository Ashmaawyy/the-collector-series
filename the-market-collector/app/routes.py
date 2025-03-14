from flask import render_template, request
from app import app
from models import get_latest_stocks, stocks_collection

PAGE_SIZE = 5

@app.route("/")
def home():
    """Main route serving the dashboard"""
    query = request.args.get("q", "").strip().upper()
    page = int(request.args.get("page", 1))
    
    try:
        # Get paginated results
        skip = (page - 1) * PAGE_SIZE
        pipeline = [
            {"$match": {"symbol": {"$regex": f".*{query}.*", "$options": "i"}}},
            {"$sort": {"timestamp": -1}},
            {"$skip": skip},
            {"$limit": PAGE_SIZE}
        ]
        
        stocks = list(stocks_collection.aggregate(pipeline))
        total_count = stocks_collection.count_documents({"symbol": {"$regex": query, "$options": "i"}})
        total_pages = (total_count + PAGE_SIZE - 1) // PAGE_SIZE
        
        return render_template("index.html", 
                             stocks=stocks,
                             page=page,
                             total_pages=total_pages,
                             query=query)
    
    except Exception as e:
        app.logger.error(f"🔥 Route error: {str(e)}")
        return render_template("error.html", message="Failed to load stock data"), 500
