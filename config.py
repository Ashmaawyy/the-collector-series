import os

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ashmawy:<db_password>@my-free-cluster.0am2f.mongodb.net/")
DB_NAME = "news_aggregator"
COLLECTION_NAME = "headlines"
