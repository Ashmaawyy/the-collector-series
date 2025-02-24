document.addEventListener("DOMContentLoaded", function () {
    const toggleSwitch = document.getElementById("theme-toggle");
    const body = document.body;
    const backToTopBtn = document.getElementById("back-to-top");
    const moonIcon = document.querySelector(".moon");
    const sunIcon = document.querySelector(".sun");
    const searchInput = document.getElementById("search-input");
    const header = document.querySelector("header");

    function applyTheme(theme) {
        if (theme === "dark") {
            body.classList.add("dark-mode");
            header.classList.add("dark-header");
            searchInput.classList.add("dark-search");
            toggleSwitch.checked = true;
            moonIcon.style.opacity = "1";
            sunIcon.style.opacity = "0.3";
        } else {
            body.classList.remove("dark-mode");
            header.classList.remove("dark-header");
            searchInput.classList.remove("dark-search");
            moonIcon.style.opacity = "0.3";
            sunIcon.style.opacity = "1";
        }
    }

    // Apply saved theme
    applyTheme(localStorage.getItem("theme") || "dark");

    // Theme toggle functionality
    toggleSwitch.addEventListener("change", function () {
        const theme = this.checked ? "dark" : "light";
        localStorage.setItem("theme", theme);
        applyTheme(theme);
    });

    // Search functionality (Enter key)
    function performSearch() {
        const query = searchInput.value.trim();
        if (query !== "") {
            fetch(`/search_stocks?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    const stocksContainer = document.getElementById("stocks-container");
                    stocksContainer.innerHTML = "";

                    data.stocks.forEach(stock => {
                        const stockCard = document.createElement("div");
                        stockCard.classList.add("stock-card", "small-stock");
                        stockCard.innerHTML = `
                            <h2>${stock.symbol}</h2>
                            <canvas id="chart-${stock.symbol}"></canvas>
                        `;
                        stocksContainer.appendChild(stockCard);

                        // Render chart
                        renderChart(stock.symbol, stock.metrics);
                    });
                });
        }
    }

    function renderChart(symbol, metrics) {
        const ctx = document.getElementById(`chart-${symbol}`).getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: metrics.map(metric => metric.timestamp),
                datasets: [{
                    label: `${symbol} Stock Price`,
                    data: metrics.map(metric => metric.close),
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        }
                    },
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }

    searchInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            performSearch();
        }
    });

    let page = 1;
    let loading = false;

    async function loadMoreStocks() {
        if (loading) return;
        loading = true;

        const response = await fetch(`/load_more_stocks?page=${page}`);
        const data = await response.json();

        if (data.stocks.length > 0) {
            const stocksContainer = document.getElementById("stocks-container");
            data.stocks.forEach(stock => {
                const stockCard = document.createElement("div");
                stockCard.classList.add("stock-card", "small-stock");
                stockCard.style.opacity = "0";

                stockCard.innerHTML = `
                    <h2>${stock.symbol}</h2>
                    <canvas id="chart-${stock.symbol}"></canvas>
                `;

                stocksContainer.appendChild(stockCard);
                setTimeout(() => stockCard.style.opacity = "1", 200);

                // Render chart
                renderChart(stock.symbol, stock.metrics);
            });

            page++;
            loading = false;
        }
    }

    window.addEventListener("scroll", function () {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
            loadMoreStocks();
        }

        if (window.scrollY > 300) {
            backToTopBtn.style.display = "block";
        } else {
            backToTopBtn.style.display = "none";
        }
    });

    backToTopBtn.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    // Pull to refresh functionality
    let touchStartY = 0;
    let touchEndY = 0;

    window.addEventListener("touchstart", function (event) {
        touchStartY = event.touches[0].clientY;
    });

    window.addEventListener("touchend", function (event) {
        touchEndY = event.changedTouches[0].clientY;
        if (touchEndY - touchStartY > 100) { // Adjust the threshold as needed
            location.reload();
        }
    });
});
