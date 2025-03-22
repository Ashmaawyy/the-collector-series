document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById('theme-toggle');
    const searchInput = document.getElementById('search-input');
    const stocksContainer = document.getElementById('stocks-container');
    const backToTopBtn = document.getElementById('back-to-top');
    let isLoading = false;
    let currentPage = 1;
    let hasMore = true;
    const seenSymbols = new Set();

    const applyTheme = (theme) => {
        document.documentElement.classList.toggle('dark-mode', theme === 'dark');
        localStorage.setItem('theme', theme);
        themeToggle.checked = theme === 'dark';
        document.documentElement.classList.add('theme-transition');
        setTimeout(() => {
            document.documentElement.classList.remove('theme-transition');
        }, 300);
    };

    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    themeToggle.addEventListener('change', (e) => {
        applyTheme(e.target.checked ? 'dark' : 'light');
    });

    const debounce = (fn, delay) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn(...args), delay);
        };
    };

    const fetchStocks = async (page, query = '') => {
        try {
            isLoading = true;
            showLoadingIndicator();
            const response = await fetch(`/api/load-more-stocks?page=${page}&q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error(response.statusText);
            const { stocks, next_page } = await response.json();
            if (stocks.length === 0) {
                hasMore = false;
                showMessage('No more stocks to load');
                return [];
            }
            currentPage = next_page || currentPage + 1;
            hasMore = !!next_page;
            return stocks;
        } catch (error) {
            hasMore = false;
            showMessage(`Error loading stocks: ${error.message}`, 'error');
            return [];
        } finally {
            isLoading = false;
            hideLoadingIndicator();
        }
    };

    const formatTimestamp = (timestamp) => {
        // Example: Convert UNIX timestamp to readable date
        return new Date(timestamp).toLocaleDateString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    };
    
    const formatCurrency = (value) => {
        // Example: Format as USD currency
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
    };
    
    const formatNumber = (value) => {
        // Used for volume formatting
        return new Intl.NumberFormat().format(value);
    };

    const createStockCard = (stock) => {
        const card = document.createElement("div");
        card.classList.add("stock-card");

        const header = document.createElement("div");
        header.classList.add("stock-header");
        header.innerHTML = `<h2>${stock.symbol}</h2><span class="timestamp">${formatTimestamp(stock.timestamp)}</span>`;

        const priceGrid = document.createElement("div");
        priceGrid.classList.add("price-grid");
        priceGrid.innerHTML = `
            <div class="price-item"><span class="label">📌 Open</span><span class="value">${formatCurrency(stock.open)}</span></div>
            <div class="price-item"><span class="label">📈 High</span><span class="value">${formatCurrency(stock.high)}</span></div>
            <div class="price-item"><span class="label">📉 Low</span><span class="value">${formatCurrency(stock.low)}</span></div>
            <div class="price-item"><span class="label">📌 Close</span><span class="value">${formatCurrency(stock.close)}</span></div>
        `;

        const volume = document.createElement("div");
        volume.classList.add("volume");
        volume.innerHTML = `📊 Volume: ${formatNumber(stock.volume)}`;

        card.appendChild(header);
        card.appendChild(priceGrid);
        card.appendChild(volume);

        return card;
    };

    const getStockSymbol = (stock) => stock.symbol || "Unknown Symbol";

    const appendStocks = (stocks) => {
        stocks.forEach(stock => {
            const card = createStockCard(stock);
            stocksContainer.appendChild(card);
            fadeInElement(card);
        });
    };

    const fadeInElement = (element) => {
        element.style.opacity = '0';
        element.style.display = 'block';
        requestAnimationFrame(() => {
            element.style.transition = 'opacity 0.3s ease-out';
            element.style.opacity = '1';
        });
    };

    const showLoadingIndicator = () => {
        const loader = document.createElement('div');
        loader.id = 'loading-indicator';
        loader.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading more stocks...';
        document.body.appendChild(loader);
    };

    const hideLoadingIndicator = () => {
        const loader = document.getElementById('loading-indicator');
        if (loader) loader.remove();
    };

    const showMessage = (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    };

    const loadMoreStocks = async () => {
        if (isLoading || !hasMore) return;
        const stocks = await fetchStocks(currentPage, searchInput.value.trim());
        appendStocks(stocks);
    };

    searchInput.addEventListener('input', debounce(async (e) => {
        currentPage = 1;
        hasMore = true;
        stocksContainer.innerHTML = '';
        seenSymbols.clear();
        const stocks = await fetchStocks(currentPage, e.target.value);
        appendStocks(stocks);
    }, 300));

    window.addEventListener('scroll', () => {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        backToTopBtn.style.display = scrollTop > 300 ? 'block' : 'none';
        if (!isLoading && hasMore && (scrollTop + clientHeight >= scrollHeight - 100)) {
            loadMoreStocks();
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    loadMoreStocks();
});
