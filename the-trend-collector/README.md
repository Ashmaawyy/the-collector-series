# 🔥 The Trend Collector

## 🌟 Overview
The Trend Collector is a **Flask-based web application** that fetches and displays **trending topics from Reddit**. It provides:
- **Live trend tracking** from Reddit’s hot topics.
- **Search functionality** to find trends in specific subreddits.
- **Dark/Light mode toggle** for better readability.
- **Infinite scrolling** for seamless updates.

## 🚀 Features
✅ **Real-time trending topics** from Reddit.  
✅ **Search by subreddit** to find trends in specific communities.  
✅ **Infinite scrolling** for continuous updates.  
✅ **Dark/Light mode switch** for user customization.  
✅ **Back to Top button** for easy navigation.  

## 🛠️ Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Data Source:** Reddit API (PRAW)

## 📜 Installation Guide
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-username/trend-collector.git
cd trend-collector
```
### 2️⃣ Install Dependencies
```sh
pip install flask praw
```
### 3️⃣ Set Up Reddit API Credentials
- Create a Reddit App at [Reddit Developer Portal](https://www.reddit.com/prefs/apps).
- Add your **client ID, client secret, and user agent** to `app.py`.

### 4️⃣ Run the Application
```sh
python app.py
```
### 5️⃣ Open in Browser
Visit **`http://127.0.0.1:5000/`** in your browser.

## 📌 Configuration
- **Modify `app.py`** to fetch more subreddit trends.
- **Customize themes** in `styles.css`.

## 🤝 Contributing
Contributions are welcome! Open an issue or submit a pull request.

## 📜 License
This project is licensed under the MIT License.