<<<<<<< HEAD
=======
# 📰 The News Collector

## 🌟 Project Overview

This project is a **modern news aggregator** that fetches and displays news articles dynamically. It features:

- **Infinite scrolling** for continuous news loading.
- **Dark/Light mode switch** for better readability.
- **Fixed header** with a **search box**.
- **Smooth "Back to Top" button**.
- **Google Scholar support** (optional) for academic articles.

## 🚀 Features

✅ **Infinite Scroll** – Automatically loads more news when scrolling down. ✅ **Search Functionality** – Type and press **Enter** to search news. ✅ **Dark & Light Mode** – Toggle between themes. ✅ **Fixed Header** – Ensures easy access to search and theme switch. ✅ **Back to Top Button** – Quickly return to the top of the page. ✅ **Fast Performance** – Fetches data dynamically using Flask & MongoDB.

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Database:** MongoDB
- **Web Scraping:** BeautifulSoup / Scholarly (for Google Scholar)

## 📜 Installation Guide

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/your-username/news-aggregator.git
cd news-aggregator
```

### 2️⃣ Install Dependencies

```sh
pip install flask pymongo scholarly requests
```

### 3️⃣ Start the Flask Server

```sh
python app.py
```

### 4️⃣ Open in Browser

Visit `` in your browser.

## 📸 Screenshots

| Light Mode | Dark Mode |
| ---------- | --------- |
|            |           |

## 🔧 Configuration

- **News API Integration:** Modify `app.py` to fetch from a specific news source.
- **Google Scholar Mode:** Set `query = "your topic"` in `fetch_scholar_articles()`.
- **Customize Themes:** Modify `styles.css` for personalized themes.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit PRs.
>>>>>>> 2bcc0b53fc3780756441dc7cdc50a878dbdbd766
