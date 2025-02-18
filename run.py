from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
API_KEY = "your_api_key"

def fetch_news(query="", category="", page=1):
    params = {
        "q": query,
        "category": category,
        "apiKey": API_KEY,
        "page": page,
        "pageSize": 5,
        "country": "us"
    }
    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code == 200:
        return response.json().get("articles", [])
    return []

@app.route("/")
def index():
    news = fetch_news()
    return render_template("index.html", news=news, page=1)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    category = request.args.get("category", "")
    page = int(request.args.get("page", 1))
    news = fetch_news(query, category, page)
    return render_template("index.html", news=news, page=page, query=query, category=category)

@app.route("/update_news")
def update_news():
    latest_news = fetch_news()
    return jsonify(latest_news)

if __name__ == "__main__":
    app.run(debug=True)
