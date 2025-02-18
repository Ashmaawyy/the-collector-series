from app import app
from app.scheduler import start_scheduler

if __name__ == "__main__":
    start_scheduler()
    app.run(debug=True)