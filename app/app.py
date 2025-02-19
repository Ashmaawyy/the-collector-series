from flask import Flask, render_template, request
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import datetime

app = Flask(__name__)

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["local"]
news_collection = db["headlines"]

def fetch_and_store_news():
    api_url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=1f44150911944ca9bb27320681169afc"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        for article in articles:
            if not news_collection.find_one({"title": article["title"]}):
                news_collection.insert_one({
                    "title": article["title"],
                    "source": article["source"]["name"],
                    "author": article.get("author", "N/A"),
                    "publishedAt": article.get("publishedAt", datetime.datetime.now()),
                    "url": article["url"],
                    "urlToImage": article.get("urlToImage", ""),
                    "category": "General"
                })
        print("News Updated!")
    else:
        print("Failed to fetch news.")

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store_news, "interval", minutes=5)
scheduler.start()

@app.route('/')
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 5
    total_count = news_collection.count_documents({})
    total_pages = (total_count + per_page - 1) // per_page
    
    news = list(news_collection.find().sort("publishedAt", -1).skip((page - 1) * per_page).limit(per_page))
    
    return render_template("index.html", news=news, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(debug=True)
