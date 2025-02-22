from flask import render_template, request
from app import app
from app.models import get_latest_trends

PAGE_SIZE = 5  # Number of trends per page

@app.route("/")
def home():
    """
    Fetches the latest social media trends from MongoDB with pagination, search, and source filtering.
    """
    query = request.args.get("q", "").strip().lower()  # Get search query
    source = request.args.get("source", "").strip().lower()  # Get source filter
    page = int(request.args.get("page", 1))  # Get current page, default to 1

    all_trends = get_latest_trends(limit=50)  # Fetch up to 50 trends
    filtered_trends = []

    # Filter trends based on search or source
    for trend in all_trends:
        name_match = query in trend["name"].lower() if query else True
        source_match = trend["source"].lower() == source if source else True

        if name_match and source_match:
            filtered_trends.append(trend)

    # Pagination logic
    total_trends = len(filtered_trends)
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    paginated_trends = filtered_trends[start_idx:end_idx]

    total_pages = (total_trends // PAGE_SIZE) + (1 if total_trends % PAGE_SIZE > 0 else 0)

    return render_template("index.html", trends=paginated_trends, query=query, source=source, page=page, total_pages=total_pages)
