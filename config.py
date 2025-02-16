import os

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "news_aggregator"
COLLECTION_NAME = "headlines"
