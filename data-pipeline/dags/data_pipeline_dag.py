from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.latest_only import LatestOnlyOperator
from datetime import datetime, timedelta
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
with DAG(
    'mongo_to_postgres_pipeline',
    default_args=default_args,
    description='A DAG to migrate data from MongoDB to PostgreSQL',
    schedule_interval=timedelta(hours=1),  # Runs every hour
    catchup=False,
) as dag:

    def create_postgres_warehouse():
        logging.info("🏗️ Creating PostgreSQL Warehouse...")
        subprocess.run(['python', 'create_warehouse.py'], check=True)
        logging.info("✅ Warehouse created successfully.")

    def migrate_data():
        logging.info("📦 Migrating data from MongoDB to PostgreSQL...")
        subprocess.run(['python', 'mongo_to_postgres.py'], check=True)
        logging.info("✅ Data migration completed.")

    # Run warehouse creation only once
    latest_only = LatestOnlyOperator(
        task_id='run_create_warehouse_once'
    )

    create_warehouse = PythonOperator(
        task_id='create_postgres_warehouse',
        python_callable=create_postgres_warehouse,
    )

    migrate_data_task = PythonOperator(
        task_id='migrate_data',
        python_callable=migrate_data,
    )

    # Define DAG execution order
    latest_only >> create_warehouse >> migrate_data_task
