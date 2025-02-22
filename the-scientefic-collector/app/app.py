from flask import Flask, render_template, request, jsonify
from scholarly import scholarly

app = Flask(__name__)

def fetch_scholar_articles(query, start=0, num_results=10):
    articles = []
    search_query = scholarly.search_pubs(query)

    for _ in range(num_results):
        try:
            pub = next(search_query)
            articles.append({
                "title": pub['bib']['title'],
                "source": pub['bib'].get('venue', 'Unknown Journal'),
                "author": ', '.join(pub['bib'].get('author', ['Unknown'])),
                "publishedAt": pub['bib'].get('pub_year', 'Unknown'),
                "url": pub.get('pub_url', '#'),
            })
        except StopIteration:
            break
    return articles

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/load_more_articles')
def load_more_articles():
    page = request.args.get("page", 1, type=int)
    query = request.args.get("query", "machine learning")
    articles = fetch_scholar_articles(query, start=(page - 1) * 10, num_results=10)
    return jsonify({"articles": articles, "page": page})

if __name__ == "__main__":
    app.run(debug=True)
