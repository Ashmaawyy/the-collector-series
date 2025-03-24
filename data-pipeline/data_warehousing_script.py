import pymongo
import psycopg2
import logging
from psycopg2.extras import execute_values

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017"
mongo_client = pymongo.MongoClient(MONGO_URI)
mongo_db = mongo_client["collector_series"]

# PostgreSQL Connection
PG_CONN = psycopg2.connect(
    dbname="collector_db",
    user="your_username",
    password="your_password",
    host="localhost",
    port="5432"
)
pg_cursor = PG_CONN.cursor()

# Function to migrate data
def migrate_collection(mongo_collection, pg_table, fields_mapping):
    mongo_data = list(mongo_collection.find({}, {"_id": 0}))
    transformed_data = [tuple(doc.get(field, None) for field in fields_mapping) for doc in mongo_data]
    
    query = f"""
        INSERT INTO {pg_table} ({', '.join(fields_mapping)})
        VALUES %s
        ON CONFLICT DO NOTHING;
    """
    execute_values(pg_cursor, query, transformed_data)
    PG_CONN.commit()
    logging.info(f"✅ Migrated {len(transformed_data)} records to {pg_table}")

# Migrate News Data
migrate_collection(mongo_db["news"], "news_articles", ["title", "source", "author", "publishedAt", "url", "urlToImage", "category"])

# Migrate Scientific Papers Data
migrate_collection(mongo_db["scientific_papers"], "scientific_papers", ["title", "author", "publishedAt", "url", "abstract", "journal"])

# Migrate Market Data (Updated Schema)
migrate_collection(mongo_db["market"], "market_data", ["symbol", "open", "high", "low", "close", "volume", "timestamp"])

# Close connections
pg_cursor.close()
PG_CONN.close()
mongo_client.close()
logging.info("✅ Database connections closed successfully.")
