from flask import render_template, request
from app import app
from app.models import get_latest_papers

PAGE_SIZE = 5  # Number of papers per page

@app.route("/")
def home():
    """
    Fetches the latest scientific papers from MongoDB with pagination, search, and category filtering.
    """
    query = request.args.get("q", "").strip().lower()  # Get search query
    category = request.args.get("category", "").strip().lower()  # Get category filter
    page = int(request.args.get("page", 1))  # Get current page, default to 1

    all_papers = get_latest_papers(limit=50)  # Fetch up to 50 papers
    filtered_papers = []

    # Filter papers based on search or category
    for paper in all_papers:
        title_match = query in paper["title"].lower() if query else True
        abstract_match = query in paper["abstract"].lower() if query else True
        category_match = paper["category"].lower() == category if category else True

        if (title_match or abstract_match) and category_match:
            filtered_papers.append(paper)

    # Pagination logic
    total_papers = len(filtered_papers)
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    paginated_papers = filtered_papers[start_idx:end_idx]

    total_pages = (total_papers // PAGE_SIZE) + (1 if total_papers % PAGE_SIZE > 0 else 0)

    return render_template("index.html", papers=paginated_papers, query=query, category=category, page=page, total_pages=total_pages)
