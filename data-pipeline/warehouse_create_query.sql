CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT,
    author TEXT,
    publishedAt TIMESTAMP,
    url TEXT UNIQUE,
    urlToImage TEXT,
    category TEXT
);

CREATE TABLE IF NOT EXISTS scientific_papers (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    publishedAt TIMESTAMP,
    url TEXT UNIQUE,
    abstract TEXT,
    journal TEXT
);

CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    open NUMERIC(10, 2),
    high NUMERIC(10, 2),
    low NUMERIC(10, 2),
    close NUMERIC(10, 2),
    volume BIGINT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
