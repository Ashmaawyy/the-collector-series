from flask import render_template, request, jsonify
from app import app
from models import get_latest_headlines, fetch_articles, store_articles, news_collection
import logging
import re

logger = logging.getLogger(__name__)

PAGE_SIZE = 8  # Number of articles per page

@app.route("/")
def home():
    """
    Fetches the latest news articles from MongoDB with pagination, search, and category filtering.
    """
    query = request.args.get("q", "").strip().lower()  # Get search query
    category = request.args.get("category", "").strip().lower()  # Get category filter
    page = int(request.args.get("page", 1))  # Get current page, default to 1

    all_articles = get_latest_headlines(limit=50)  # Fetch up to 50 articles
    filtered_articles = []

    # Filter articles based on search or category
    for article in all_articles:
        headline_match = query in article["title"].lower() if query else True
        category_match = article["category"].lower() == category if category else True

        if headline_match and category_match:
            filtered_articles.append(article)

    # Pagination logic
    total_articles = len(filtered_articles)
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    paginated_articles = filtered_articles[start_idx:end_idx]

    total_pages = (total_articles // PAGE_SIZE) + (1 if total_articles % PAGE_SIZE > 0 else 0)

    return render_template("index.html", articles=paginated_articles, query=query, category=category, page=page, total_pages=total_pages)

@app.route('/update_news', methods=['GET'])
def update_news():
    logger.info("🔄 Manual news update triggered")
    try:
        articles = fetch_articles()
        store_articles(articles)
        return jsonify({"status": "success", "message": "News updated!"})
    except Exception as e:
        logger.error(f"❌ Manual update failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

"""@app.route('/load_latest_news')
def load_latest_news():
    logger.debug("📥 Loading latest news")
    latest_news = list(news_collection.find().sort("publishedAt", -1).limit(5))

    news_data = [
        {
            "title": item.get("title", "No Title"),
            "source": item.get("source", "Unknown"),
            "author": item.get("author", "N/A"),
            "publishedAt": item["publishedAt"] if isinstance(item["publishedAt"], str) else item["publishedAt"].strftime("%Y-%m-%d %H:%M:%S"),
            "url": item["url"],
            "urlToImage": item.get("urlToImage", ""),
            "summary": item.get("summary", "No summary available.")
        } for item in latest_news
    ]

    return jsonify({"news": news_data})
"""
@app.route('/load_more_news')
def load_more_news():
    page = request.args.get("page", 1, type=int)
    logger.info(f"📖 Loading more news (page {page})")
    per_page = 8

    news = list(news_collection.find().sort("publishedAt", -1).skip((page - 1) * per_page).limit(per_page))

    news_data = [
        {
            "title": item.get("title", "No Title"),
            "source": item.get("source", "Unknown"),
            "author": item.get("author", "N/A"),
            "publishedAt": item["publishedAt"] if isinstance(item["publishedAt"], str) else item["publishedAt"].strftime("%Y-%m-%d %H:%M:%S"),
            "url": item["url"],
            "urlToImage": item.get("urlToImage", ""),
        } for item in news
    ]

    return jsonify({"news": news_data, "page": page})

@app.route('/search_news')
def search_news():
    query = re.escape(request.args.get("q", "").strip().lower())
    logger.info(f"🔍 Searching for: '{query}'")
    try:
        news_collection.create_index([("title", "text")])
        news = list(news_collection.find({"$text": {"$search": query}}).limit(10))
        
        logger.info(f"🔎 Found {len(news)} results for '{query}'")
        news_data = [
            {
                "title": item.get("title", "No Title"),
                "source": item.get("source", "Unknown"),
                "author": item.get("author", "N/A"),
                "publishedAt": item.get("publishedAt", ""),
                "url": item["url"],
                "urlToImage": item.get("urlToImage", ""),
            } for item in news
        ]
        return jsonify({"news": news_data})
    except Exception as e:
        logger.error(f"❌ Search failed: {str(e)}")
        return jsonify({"news": []})
