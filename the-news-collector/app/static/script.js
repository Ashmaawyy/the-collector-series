document.addEventListener("DOMContentLoaded", function () {
    const toggleSwitch = document.getElementById("theme-toggle");
    const body = document.body;
    const backToTopBtn = document.getElementById("back-to-top");
    const moonIcon = document.querySelector(".moon");
    const sunIcon = document.querySelector(".sun");
    const searchInput = document.getElementById("search-input");
    const header = document.querySelector("header");
    const loadingSpinner = document.getElementById("loading-spinner");

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

    // Show loading spinner
    function showLoadingSpinner() {
        loadingSpinner.style.display = "flex";
    }

    // Hide loading spinner
    function hideLoadingSpinner() {
        loadingSpinner.style.display = "none";
    }

    // Search functionality (Enter key)
    function performSearch() {
        const query = searchInput.value.trim();
        if (query !== "") {
            showLoadingSpinner();
            fetch(`/search_news?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    const newsContainer = document.getElementById("news-container");
                    newsContainer.innerHTML = "";

                    data.news.forEach(article => {
                        const newsCard = document.createElement("div");
                        newsCard.classList.add("news-card", "small-news");
                        newsCard.innerHTML = `
                            <h2>${article.title || "No Title"}</h2>
                            <div class="news-meta">
                                <span><i class="fas fa-user"></i> ${article.author || "Unknown"}</span>
                                <span><i class="fas fa-calendar-alt"></i> ${new Date(article.publishedAt).toLocaleDateString()}</span>
                            </div>
                            ${article.urlToImage ? `<img src="${article.urlToImage}" alt="News Image" class="news-image small-news-image">` : ""}
                            <a href="${article.url}" target="_blank" class="news-link">
                                Read Full Article <i class="fas fa-external-link-alt"></i>
                            </a>
                        `;
                        newsContainer.appendChild(newsCard);
                    });
                    hideLoadingSpinner();
                })
                .catch(error => {
                    console.error("Error fetching news:", error);
                    hideLoadingSpinner();
                });
        }
    }

    searchInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            performSearch();
        }
    });

    let page = 1;
    let loading = false;

    let seenUrls = new Set(); // Track loaded articles

    async function loadMoreNews() {
        if (loading) return;
        loading = true;
        showLoadingSpinner();

        const response = await fetch(`/load_more_news?page=${page}`);
        const data = await response.json();

        if (data.news.length > 0) {
            const newsContainer = document.getElementById("news-container");
            data.news.forEach(article => {
                if (!seenUrls.has(article.url)) { // Check for duplicates
                    seenUrls.add(article.url);
                    const newsCard = document.createElement("div");
                    newsCard.classList.add("news-card", "small-news");
                    newsCard.innerHTML = `
                        <h2>${article.title || "No Title"}</h2>
                        <div class="news-meta">
                            <span><i class="fas fa-user"></i> ${article.author || "Unknown"}</span>
                            <span><i class="fas fa-calendar-alt"></i> ${new Date(article.publishedAt).toLocaleDateString()}</span>
                        </div>
                        ${article.urlToImage ? `<img src="${article.urlToImage}" alt="News Image" class="news-image small-news-image">` : ""}
                        <a href="${article.url}" target="_blank" class="news-link">
                            Read Full Article <i class="fas fa-external-link-alt"></i>
                        </a>
                    `;
                    newsContainer.appendChild(newsCard);
                }
            });

            page++;
            loading = false;
            hideLoadingSpinner();
        }
    }

    window.addEventListener("scroll", function () {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
            loadMoreNews();
        }

        if (window.scrollY > 300) {
            backToTopBtn.style.display = "inline";
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

    // Initial load
    loadMoreNews();
});
