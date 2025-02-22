from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import datetime
import tweepy
import praw  # Reddit API
from googleapiclient.discovery import build  # YouTube API

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
twitter_api = tweepy.API(auth)

# Reddit API Setup
reddit = praw.Reddit(client_id='YOUR_REDDIT_CLIENT_ID',
                     client_secret='YOUR_REDDIT_CLIENT_SECRET',
                     user_agent='YOUR_USER_AGENT')

# YouTube API Setup
youtube_api_key = "YOUR_YOUTUBE_API_KEY"
youtube = build('youtube', 'v3', developerKey=youtube_api_key)

def fetch_and_store_twitter_trends():
    try:
        trends = twitter_api.get_place_trends(id=1)  # WOEID 1 is for worldwide trends
        if trends:
            for trend in trends[0]["trends"]:
                if not trends_collection.find_one({"name": trend["name"], "source": "Twitter"}):
                    trends_collection.insert_one({
                        "name": trend["name"],
                        "url": trend["url"],
                        "tweet_volume": trend.get("tweet_volume", "N/A"),
                        "timestamp": datetime.datetime.now(),
                        "source": "Twitter"
                    })
            print("Twitter Trends Updated!")
        else:
            print("No Twitter trends found.")
    except Exception as e:
        print(f"Failed to fetch Twitter trends: {e}")

def fetch_and_store_reddit_trends():
    try:
        subreddit = reddit.subreddit('all')
        for submission in subreddit.hot(limit=10):
            if not trends_collection.find_one({"name": submission.title, "source": "Reddit"}):
                trends_collection.insert_one({
                    "name": submission.title,
                    "url": submission.url,
                    "tweet_volume": submission.score,
                    "timestamp": datetime.datetime.now(),
                    "source": "Reddit"
                })
        print("Reddit Trends Updated!")
    except Exception as e:
        print(f"Failed to fetch Reddit trends: {e}")

def fetch_and_store_youtube_trends():
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            chart="mostPopular",
            regionCode="US",
            maxResults=10
        )
        response = request.execute()
        for item in response['items']:
            if not trends_collection.find_one({"name": item['snippet']['title'], "source": "YouTube"}):
                trends_collection.insert_one({
                    "name": item['snippet']['title'],
                    "url": f"https://www.youtube.com/watch?v={item['id']}",
                    "tweet_volume": item['statistics']['viewCount'],
                    "timestamp": datetime.datetime.now(),
                    "source": "YouTube"
                })
        print("YouTube Trends Updated!")
    except Exception as e:
        print(f"Failed to fetch YouTube trends: {e}")

def fetch_and_store_trends():
    fetch_and_store_twitter_trends()
    fetch_and_store_reddit_trends()
    fetch_and_store_youtube_trends()

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
            "timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "source": item["source"]
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
            "timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "source": item["source"]
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
            "timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "source": item["source"]
        } for item in trends
    ]

    return jsonify({"trends": trends_data})

if __name__ == "__main__":
    app.run(debug=True)
