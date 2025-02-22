import requests
from bs4 import BeautifulSoup
from app.models import store_headlines
import requests
from bs4 import BeautifulSoup

def scrape_news(source):
    """
    Scrapes news data from a given source dictionary.
    Returns a list of dictionaries containing extracted data.
    """
    try:
        response = requests.get(source["url"], headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all(source["headline_tag"])

        scraped_data = []

        for article in articles[:10]:  # Limit to 10 articles per source
            news_item = {}

            # Extract headline text
            news_item["headline"] = article.get_text(strip=True)

            # Extract article URL
            link_tag = article.find(source["article_url_tag"])
            if link_tag and link_tag.has_attr("href"):
                news_item["article_url"] = link_tag["href"]
            else:
                news_item["article_url"] = "N/A"

            # Extract publication date
            if source.get("publication_date_tag"):
                date_tag = soup.find(source["publication_date_tag"])
                if date_tag:
                    news_item["publication_date"] = date_tag.get(source.get("publication_date_attr", ""), "").strip()
                else:
                    news_item["publication_date"] = "N/A"

            # Extract author
            if source.get("author_tag") and source.get("author_class"):
                author_tag = soup.find(source["author_tag"], class_=source["author_class"])
                news_item["author"] = author_tag.get_text(strip=True) if author_tag else "N/A"

            # Extract summary
            if source.get("summary_tag") and source.get("summary_class"):
                summary_tag = soup.find(source["summary_tag"], class_=source["summary_class"])
                news_item["summary"] = summary_tag.get_text(strip=True) if summary_tag else "N/A"

            # Extract category
            if source.get("category_tag") and source.get("category_class"):
                category_tag = soup.find(source["category_tag"], class_=source["category_class"])
                news_item["category"] = category_tag.get_text(strip=True) if category_tag else "N/A"

            # Extract image URL
            if source.get("image_tag") and source.get("image_attr"):
                image_tag = soup.find(source["image_tag"])
                news_item["image_url"] = image_tag[source["image_attr"]] if image_tag and image_tag.has_attr(source["image_attr"]) else "N/A"

            # Extract keywords
            if source.get("keywords_tag") and source.get("keywords_attr"):
                meta_keywords = soup.find(source["keywords_tag"], attrs={source["keywords_attr"]: True})
                news_item["keywords"] = meta_keywords[source["keywords_attr"]] if meta_keywords else "N/A"

            scraped_data.append(news_item)

        return scraped_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {source['name']}: {e}")
        return []

def scrape_all():
    """Scrapes multiple news sources"""
    sources = [
    {
        "name": "BBC",
        "url": "https://www.bbc.com/news",
        "headline_tag": "h2",
        "article_url_tag": "a",
        "publication_date_tag": "time",
        "publication_date_attr": "datetime",
        "author_tag": "span",
        "author_class": "byline__name",
        "summary_tag": "p",
        "category_tag": "a",
        "category_class": "nw-c-nav__wide-menuitem",
        "image_tag": "img",
        "image_attr": "src",
        "keywords_tag": "meta",
        "keywords_attr": "content"
    },
    {
        "name": "CNN",
        "url": "https://edition.cnn.com/world",
        "headline_tag": "h2",
        "article_url_tag": "a",
        "publication_date_tag": "span",
        "publication_date_class": "date",
        "author_tag": "span",
        "author_class": "metadata__byline__author",
        "summary_tag": "div",
        "summary_class": "zn-body__paragraph",
        "category_tag": "a",
        "category_class": "section-nav__link",
        "image_tag": "img",
        "image_attr": "data-src",
        "keywords_tag": "meta",
        "keywords_attr": "content"
    },
    {
        "name": "Reuters",
        "url": "https://www.reuters.com/",
        "headline_tag": "h2",
        "article_url_tag": "a",
        "publication_date_tag": "time",
        "publication_date_attr": "datetime",
        "author_tag": "span",
        "author_class": "Byline-name",
        "summary_tag": "p",
        "summary_class": "article-summary",
        "category_tag": "a",
        "category_class": "section-link",
        "image_tag": "img",
        "image_attr": "src",
        "keywords_tag": "meta",
        "keywords_attr": "name"
    },
    {
        "name": "New York Times",
        "url": "https://www.nytimes.com/",
        "headline_tag": "h2",
        "article_url_tag": "a",
        "publication_date_tag": "time",
        "publication_date_attr": "datetime",
        "author_tag": "span",
        "author_class": "css-1n7hynb",
        "summary_tag": "p",
        "summary_class": "css-axufdj",
        "category_tag": "a",
        "category_class": "css-1wjnrbv",
        "image_tag": "img",
        "image_attr": "src",
        "keywords_tag": "meta",
        "keywords_attr": "content"
    },
    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.com/",
        "headline_tag": "h2",
        "article_url_tag": "a",
        "publication_date_tag": "time",
        "publication_date_attr": "datetime",
        "author_tag": "span",
        "author_class": "author",
        "summary_tag": "p",
        "summary_class": "article-summary",
        "category_tag": "a",
        "category_class": "menu-category",
        "image_tag": "img",
        "image_attr": "data-src",
        "keywords_tag": "meta",
        "keywords_attr": "name"
    },
    {
        "name": "Fox News",
        "url": "https://www.foxnews.com/",
        "headline_tag": "h2",
        "article_url_tag": "a",
        "publication_date_tag": "time",
        "publication_date_attr": "datetime",
        "author_tag": "span",
        "author_class": "author-byline",
        "summary_tag": "p",
        "summary_class": "dek",
        "category_tag": "a",
        "category_class": "category-label",
        "image_tag": "img",
        "image_attr": "src",
        "keywords_tag": "meta",
        "keywords_attr": "keywords"
    }
    ]

    for source in sources:
        news = scrape_news(source)
    
        if news:
            store_headlines(source["name"], news)
            #print(f"\n📰 {source['name']} News:\n", news)
            print("Scraping completed successfully ; )")
