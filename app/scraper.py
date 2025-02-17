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
    {"name": "BBC", "url": "https://www.bbc.com/news", "tag": "h3"},  # BBC uses <h3> for article headlines
    {"name": "CNN", "url": "https://edition.cnn.com/world", "tag": "h2"},  # CNN uses <h2> for headlines
    {"name": "New York Times", "url": "https://www.nytimes.com/", "tag": "h2"},  # NYT uses <h2> for headlines
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/", "tag": "h2"},  # Al Jazeera uses <h2> for headlines
    {"name": "Fox News", "url": "https://www.foxnews.com/", "tag": "h2"},  # Fox News uses <h2> for headlines
    {"name": "The Guardian", "url": "https://www.theguardian.com/international", "tag": "h3"},  # The Guardian uses <h3> for headlines
    {"name": "Bloomberg", "url": "https://www.bloomberg.com", "tag": "h1"},  # Bloomberg uses <h1> for headlines
    {"name": "The Independent", "url": "https://www.independent.co.uk/", "tag": "h2"},  # The Independent uses <h2> for headlines
    {"name": "Washington Post", "url": "https://www.washingtonpost.com/", "tag": "h2"},  # Washington Post uses <h2> for headlines
    {"name": "NPR", "url": "https://www.npr.org/", "tag": "h2"},  # NPR uses <h2> for headlines
    {"name": "Associated Press", "url": "https://apnews.com/", "tag": "h1"},  # AP News uses <h1> for headlines
    {"name": "USA Today", "url": "https://www.usatoday.com/", "tag": "h2"},  # USA Today uses <h2> for headlines
    {"name": "Politico", "url": "https://www.politico.com/", "tag": "h2"},  # Politico uses <h2> for headlines
    {"name": "The Wall Street Journal", "url": "https://www.wsj.com/", "tag": "h2"},  # WSJ uses <h2> for headlines
    {"name": "The Economist", "url": "https://www.economist.com/", "tag": "h3"},  # The Economist uses <h3> for headlines
    {"name": "Time", "url": "https://time.com/", "tag": "h2"},  # Time uses <h2> for headlines
    {"name": "Forbes", "url": "https://www.forbes.com/", "tag": "h2"},  # Forbes uses <h2> for headlines
    {"name": "CNBC", "url": "https://www.cnbc.com/", "tag": "h1"},  # CNBC uses <h1> for headlines
    {"name": "The Hill", "url": "https://thehill.com/", "tag": "h2"},  # The Hill uses <h2> for headlines
    {"name": "Axios", "url": "https://www.axios.com/", "tag": "h2"},  # Axios uses <h2> for headlines
    {"name": "Vox", "url": "https://www.vox.com/", "tag": "h2"},  # Vox uses <h2> for headlines
    {"name": "BuzzFeed News", "url": "https://www.buzzfeednews.com/", "tag": "h2"},  # BuzzFeed News uses <h2> for headlines
    {"name": "The Atlantic", "url": "https://www.theatlantic.com/", "tag": "h2"},  # The Atlantic uses <h2> for headlines
    {"name": "Wired", "url": "https://www.wired.com/", "tag": "h2"},  # Wired uses <h2> for headlines
    {"name": "TechCrunch", "url": "https://techcrunch.com/", "tag": "h2"},  # TechCrunch uses <h2> for headlines
    {"name": "Ars Technica", "url": "https://arstechnica.com/", "tag": "h2"},  # Ars Technica uses <h2> for headlines
    {"name": "The Verge", "url": "https://www.theverge.com/", "tag": "h2"},  # The Verge uses <h2> for headlines
    {"name": "Mashable", "url": "https://mashable.com/", "tag": "h2"},  # Mashable uses <h2> for headlines
    {"name": "Engadget", "url": "https://www.engadget.com/", "tag": "h2"}  # Engadget uses <h2> for headlines
]
    
    for source in sources:
        headlines = scrape_website(source["url"], source["tag"])
        if headlines:
            store_headlines(source["name"], headlines)

    print("Scraping completed successfully ; )")
