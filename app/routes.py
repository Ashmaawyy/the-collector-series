from flask import render_template
from app import app
from app.models import get_latest_headlines

@app.route("/")
def home():
    """
    Fetches the latest news articles from MongoDB and passes them to the template.
    """
    articles = get_latest_headlines(limit=10)  # Fetch latest 10 articles
    return render_template("index.html", articles=articles)
