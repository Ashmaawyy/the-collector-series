document.addEventListener("DOMContentLoaded", function () {
    // Configuration
    const PAGE_SIZE = 15; // Increased page size
    const SCROLL_THRESHOLD = 100;
    const LOAD_DELAY = 200;
    
    // DOM Elements
    const stocksContainer = document.getElementById("stocks-container");
    const searchInput = document.getElementById("search-input");
    const backToTopBtn = document.getElementById("back-to-top");
    const themeToggle = document.getElementById("theme-toggle");
    const loadingIndicator = document.createElement('div');
    
    // State Management
    let currentPage = 1;
    let isLoading = false;
    let hasMore = true;

    // Initialize loading indicator
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '🔄 Loading more stocks...';
    document.body.appendChild(loadingIndicator);

    // Initial load
    loadMoreStocks();

    // Theme Toggle Functionality
    function handleThemeToggle() {
        const theme = themeToggle.checked ? 'dark' : 'light';
        localStorage.setItem('theme', theme);
        document.body.classList.toggle('dark-mode', theme === 'dark');
        document.querySelector('header').classList.toggle('dark-header', theme === 'dark');
        searchInput.classList.toggle('dark-search', theme === 'dark');
    }

    // Apply saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.classList.add(savedTheme === 'dark' ? 'dark-mode' : 'light-mode');
    themeToggle.checked = savedTheme === 'dark';
    handleThemeToggle();
    
    // Event Listeners
    themeToggle.addEventListener('change', handleThemeToggle);
    
    searchInput.addEventListener('input', debounce(() => {
        currentPage = 1;
        hasMore = true;
        stocksContainer.innerHTML = '';
        loadMoreStocks();
    }, 300));

    window.addEventListener('scroll', () => {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        
        backToTopBtn.style.display = scrollTop > 300 ? 'block' : 'none';

        if (scrollTop + clientHeight >= scrollHeight - SCROLL_THRESHOLD && !isLoading && hasMore) {
            loadMoreStocks();
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Core Loading Function
    async function loadMoreStocks() {
        if (isLoading || !hasMore) return;
        
        try {
            isLoading = true;
            loadingIndicator.style.display = 'block';

            const response = await fetch(
                `/load_more_stocks?page=${currentPage}&q=${encodeURIComponent(searchInput.value.trim())}`
            );

            if (!response.ok) throw new Error('Network response was not ok');
            
            const { stocks } = await response.json();
            
            if (stocks.length === 0) {
                hasMore = false;
                showMessage('✅ Reached end of stock data');
                return;
            }

            stocks.forEach(stock => {
                const stockCard = createStockCard(stock);
                stocksContainer.appendChild(stockCard);
                setTimeout(() => stockCard.style.opacity = 1, LOAD_DELAY);
            });

            currentPage++;
        } catch (error) {
            console.error('Failed to load stocks:', error);
            showMessage('❌ Failed to load more stocks');
        } finally {
            isLoading = false;
            loadingIndicator.style.display = 'none';
        }
    }

    // Helper Functions
    function createStockCard(stock) {
        const card = document.createElement('div');
        card.className = 'stock-card small-stock';
        card.style.opacity = '0';
        card.innerHTML = `
            <div class="stock-header">
                <h2>${stock.symbol}</h2>
                <span class="timestamp">${formatTimestamp(stock.timestamp)}</span>
            </div>
            <div class="price-grid">
                <div class="price-item">
                    <span class="label">📌 Open</span>
                    <span class="value">${formatCurrency(stock.open)}</span>
                </div>
                <div class="price-item">
                    <span class="label">📈 High</span>
                    <span class="value">${formatCurrency(stock.high)}</span>
                </div>
                <div class="price-item">
                    <span class="label">📉 Low</span>
                    <span class="value">${formatCurrency(stock.low)}</span>
                </div>
                <div class="price-item">
                    <span class="label">📌 Close</span>
                    <span class="value">${formatCurrency(stock.close)}</span>
                </div>
            </div>
            <div class="volume">
                📊 Volume: ${formatNumber(stock.volume)}
            </div>
        `;
        return card;
    }

    function formatCurrency(value) {
        return `$${parseFloat(value).toFixed(2)}`;
    }

    function formatNumber(value) {
        return parseInt(value).toLocaleString();
    }

    function formatTimestamp(ts) {
        const date = new Date(ts);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    function debounce(func, timeout = 300) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => func.apply(this, args), timeout);
        };
    }

    function showMessage(text) {
        const msg = document.createElement('div');
        msg.className = 'status-message';
        msg.textContent = text;
        document.body.appendChild(msg);
        setTimeout(() => msg.remove(), 3000);
    }
});
