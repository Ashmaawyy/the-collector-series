from flask import render_template
from app import app
from app.models import get_latest_headlines

@app.route("/")
def home():
    headlines = get_latest_headlines()
    return render_template("index.html", headlines=headlines)
