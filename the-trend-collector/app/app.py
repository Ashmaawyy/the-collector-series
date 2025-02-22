from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import datetime
import tweepy

app = Flask(__name__)

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["the-trend-collector"]
trends_collection = db["social-media-trends"]

# Twitter API Setup
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
access_token = "YOUR_ACCESS_TOKEN"
access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"

auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)

def fetch_and_store_trends():
    try:
        trends = api.get_place_trends(id=1)  # WOEID 1 is for worldwide trends
        if trends:
            for trend in trends[0]["trends"]:
                if not trends_collection.find_one({"name": trend["name"]}):
                    trends_collection.insert_one({
                        "name": trend["name"],
                        "url": trend["url"],
                        "tweet_volume": trend.get("tweet_volume", "N/A"),
                        "timestamp": datetime.datetime.now()
                    })
            print("Trends Updated!")
        else:
            print("No trends found.")
    except Exception as e:
        print(f"Failed to fetch trends: {e}")

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store_trends, "interval", minutes=60)
scheduler.start()

@app.route('/')
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 5
    total_count = trends_collection.count_documents({})
    total_pages = (total_count + per_page - 1) // per_page
    
    trends = list(trends_collection.find().sort("timestamp", -1).skip((page - 1) * per_page).limit(per_page))
    
    return render_template("index.html", trends=trends, page=page, total_pages=total_pages)

@app.route('/update_trends', methods=['GET'])
def update_trends():
    fetch_and_store_trends()
    return jsonify({"status": "success", "message": "Trends updated!"})

@app.route('/load_latest_trends')
def load_latest_trends():
    latest_trends = list(trends_collection.find().sort("timestamp", -1).limit(5))

    trends_data = [
        {
            "name": item["name"],
            "url": item["url"],
            "tweet_volume": item.get("tweet_volume", "N/A"),
            "timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        } for item in latest_trends
    ]

    return jsonify({"trends": trends_data})

@app.route('/load_more_trends')
def load_more_trends():
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Load more trends per scroll

    trends = list(trends_collection.find().sort("timestamp", -1).skip((page - 1) * per_page).limit(per_page))

    trends_data = [
        {
            "name": item["name"],
            "url": item["url"],
            "tweet_volume": item.get("tweet_volume", "N/A"),
            "timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        } for item in trends
    ]

    return jsonify({"trends": trends_data, "page": page})

@app.route('/search_trends')
def search_trends():
    query = request.args.get("q", "").lower()
    trends = list(trends_collection.find({"name": {"$regex": query, "$options": "i"}}).limit(10))

    trends_data = [
        {
            "name": item["name"],
            "url": item["url"],
            "tweet_volume": item.get("tweet_volume", "N/A"),
            "timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        } for item in trends
    ]

    return jsonify({"trends": trends_data})

if __name__ == "__main__":
    app.run(debug=True)
