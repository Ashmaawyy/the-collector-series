from flask import Flask
import pymongo
from config import MONGO_URI, DB_NAME

# Initialize Flask App
app = Flask(__name__)

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

from app import routes  # Import routes
