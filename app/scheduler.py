from flask_apscheduler import APScheduler
from app.scraper import scrape_all

scheduler = APScheduler()

def scheduled_scraping():
    scrape_all()

def start_scheduler():
    """Starts the Flask Scheduler"""
    scheduler.add_job(id="ScheduledScraping", func=scheduled_scraping, trigger="interval", minutes=1)
    scheduler.start()
