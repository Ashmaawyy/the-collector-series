# The Scientific Collector

## Project Overview
The Scientific Collector is a web application that collects and displays scientific papers from Google Scholar. It features:
- **Infinite scrolling** for seamless paper loading.
- **Search functionality** to find specific research topics.
- **Dark/Light mode toggle** for user-friendly reading.
- **Fixed header** with theme switch and search bar.
- **Back to Top button** for easy navigation.

## File Structure
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

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Data Source:** Google Scholar via `scholarly` package

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/scientific-collector.git
   cd scientific-collector
   ```
2. Install dependencies:
   ```sh
   pip install flask scholarly requests
   ```
3. Run the application:
   ```sh
   python app.py
   ```
4. Open in browser:
   ```
http://127.0.0.1:5000/
   ```
