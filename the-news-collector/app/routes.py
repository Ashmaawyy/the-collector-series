from flask import render_template, request
from app import app
from app.models import get_latest_headlines

PAGE_SIZE = 5  # Number of articles per page

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
        headline_match = query in article["headline"].lower() if query else True
        summary_match = query in article["summary"].lower() if query else True
        category_match = article["category"].lower() == category if category else True

        if (headline_match or summary_match) and category_match:
            filtered_articles.append(article)

    # Pagination logic
    total_articles = len(filtered_articles)
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    paginated_articles = filtered_articles[start_idx:end_idx]

    total_pages = (total_articles // PAGE_SIZE) + (1 if total_articles % PAGE_SIZE > 0 else 0)

    return render_template("index.html", articles=paginated_articles, query=query, category=category, page=page, total_pages=total_pages)
