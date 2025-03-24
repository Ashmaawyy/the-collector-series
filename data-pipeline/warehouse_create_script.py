import psycopg2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection details
DB_NAME = "collector_db"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"

# Read SQL file
SQL_FILE = "postgres_ddl.sql"
with open(SQL_FILE, "r") as file:
    sql_commands = file.read()

# Connect to PostgreSQL and execute the SQL file
def create_warehouse():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(sql_commands)
        conn.commit()
        logging.info("✅ PostgreSQL Warehouse Created Successfully!")
    except Exception as e:
        logging.error(f"❌ Error creating warehouse: {e}")
    finally:
        cursor.close()
        conn.close()
        logging.info("✅ Database connection closed.")

# Run the function
if __name__ == "__main__":
    create_warehouse()
