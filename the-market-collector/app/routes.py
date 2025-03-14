from flask import render_template, request, jsonify
from app import app
from models import stocks_collection, get_latest_stocks

PAGE_SIZE = 5

@app.route("/")
def home():
    query = request.args.get("q", "").strip().upper()
    symbol = request.args.get("symbol", "").strip().upper()
    page = int(request.args.get("page", 1))

    all_stocks = get_latest_stocks(limit=50)
    filtered_stocks = []

    for stock in all_stocks:
        symbol_match = query in stock["symbol"].upper() if query else True
        symbol_filter_match = stock["symbol"].upper() == symbol if symbol else True

        if symbol_match and symbol_filter_match:
            filtered_stocks.append(stock)

    total_stocks = len(filtered_stocks)
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    paginated_stocks = filtered_stocks[start_idx:end_idx]

    total_pages = (total_stocks // PAGE_SIZE) + (1 if total_stocks % PAGE_SIZE > 0 else 0)

    return render_template("index.html", 
                         stocks=paginated_stocks,
                         query=query,
                         symbol=symbol,
                         page=page,
                         total_pages=total_pages)
