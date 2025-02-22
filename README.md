# The Collector Series

## 1️⃣ The Scientific Collector
The Scientific Collector is a web application that collects and displays scientific papers from Google Scholar. It features:
- **Infinite scrolling** for seamless paper loading.
- **Search functionality** to find specific research topics.
- **Dark/Light mode toggle** for user-friendly reading.
- **Fixed header** with theme switch and search bar.
- **Back to Top button** for easy navigation.

### File Structure
```
scientific_collector/
│── app.py              # Flask backend
│── templates/
│   ├── index.html      # Frontend UI
│── static/
│   ├── styles.css      # Styling
│   ├── script.js       # Frontend logic
│── requirements.txt    # Dependencies
│── README.md           # Project documentation
```

### Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Data Source:** Google Scholar via `scholarly` package

## 2️⃣ The Market Collector
The Market Collector fetches real-time stock market and cryptocurrency data. It features:
- **Live stock and crypto price tracking**.
- **Historical data visualization**.
- **Dark/Light mode toggle** for readability.
- **Fixed header** for easy navigation.

### File Structure
```
market_collector/
│── app.py              # Flask backend
│── templates/
│   ├── index.html      # Frontend UI
│── static/
│   ├── styles.css      # Styling
│   ├── script.js       # Frontend logic
│── requirements.txt    # Dependencies
│── README.md           # Project documentation
```

### Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Data Sources:** Alpha Vantage, Yahoo Finance API

## 3️⃣ The Trend Collector
The Trend Collector gathers trending topics from social media platforms like Twitter and Reddit. It features:
- **Real-time trending topics from Twitter and Reddit**.
- **Sentiment analysis for trending discussions**.
- **Dark/Light mode toggle**.
- **Infinite scrolling for continuous updates**.

### File Structure
```
trend_collector/
│── app.py              # Flask backend
│── templates/
│   ├── index.html      # Frontend UI
│── static/
│   ├── styles.css      # Styling
│   ├── script.js       # Frontend logic
│── requirements.txt    # Dependencies
│── README.md           # Project documentation
```

### Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Data Sources:** Twitter API, Reddit API

## Installation Guide
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-username/collector-series.git
cd collector-series
```
### 2️⃣ Install Dependencies
```sh
pip install flask scholarly requests alpha_vantage praw tweepy
```
### 3️⃣ Run the Desired Collector
- **Scientific Collector:**
  ```sh
  cd scientific_collector
  python app.py
  ```
- **Market Collector:**
  ```sh
  cd market_collector
  python app.py
  ```
- **Trend Collector:**
  ```sh
  cd trend_collector
  python app.py
  ```

### 4️⃣ Open in Browser
Visit **`http://127.0.0.1:5000/`** to access the collector of your choice.

## Future Enhancements
- **More Data Sources:** Expand the number of APIs.
- **User Personalization:** Allow users to filter and save trends.
- **Dashboard Analytics:** Provide visual reports for collected data.

## 🤝 Contributing
Contributions are welcome! Feel free to open issues or submit PRs.

## 📜 License
This project is licensed under the MIT License.
