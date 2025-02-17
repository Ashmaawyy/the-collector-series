import requests
from bs4 import BeautifulSoup
from app.models import store_headlines

def scrape_website(url, tag):
    """Scrapes news headlines from a given website"""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        print(response.status_code)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = [headline.text.strip() for headline in soup.find_all(tag)]
        print(headlines[:1])
        return headlines[:10]  # Limit to top 10 headlines
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def scrape_all():
    """Scrapes multiple news sources"""
    sources = [
        {"name": "BBC", "url": "https://www.bbc.com/news", "tag": "h2"},
        {"name": "CNN", "url": "https://edition.cnn.com/world", "tag": "h2"},
        {"name": "Reuters", "url": "https://www.reuters.com/", "tag": "h2"}
    ]
    
    for source in sources:
        headlines = scrape_website(source["url"], source["tag"])
        if headlines:
            store_headlines(source["name"], headlines)

    print("Scraping completed successfully ; )")
