document.addEventListener("DOMContentLoaded", function () {
    const toggleSwitch = document.getElementById("theme-toggle");
    const body = document.body;
    const updateNewsBtn = document.getElementById("update-news");
    const backToTopBtn = document.getElementById("back-to-top");
    const moonIcon = document.querySelector(".moon");
    const sunIcon = document.querySelector(".sun");

 // Default to dark mode
 if (localStorage.getItem("theme") !== "light") {
    body.classList.add("dark-mode");
    toggleSwitch.checked = true;
    moonIcon.style.opacity = "1";
    sunIcon.style.opacity = "0.3";
} else {
    moonIcon.style.opacity = "0.3";
    sunIcon.style.opacity = "1";
}

toggleSwitch.addEventListener("change", function () {
    if (this.checked) {
        body.classList.add("dark-mode");
        localStorage.setItem("theme", "dark");
        moonIcon.style.opacity = "1";
        sunIcon.style.opacity = "0.3";
    } else {
        body.classList.remove("dark-mode");
        localStorage.setItem("theme", "light");
        moonIcon.style.opacity = "0.3";
        sunIcon.style.opacity = "1";
    }
});

updateNewsBtn.addEventListener("scroll", function () {
    fetch("/update_news").then(response => response.json()).then(data => {
        alert("News Updated!");
        location.reload();
    });
});
});

document.addEventListener("DOMContentLoaded", function () {
    let page = 1;
    let loading = false;

    async function loadMoreNews() {
        if (loading) return;
        loading = true;

        const response = await fetch(`/load_more_news?page=${page}`);
        const data = await response.json();

        if (data.news.length > 0) {
            const newsContainer = document.getElementById("news-container");
            data.news.forEach(article => {
                const newsCard = document.createElement("div");
                newsCard.classList.add("news-card", "small-news");
                newsCard.style.opacity = "0"; // Initial fade effect

                newsCard.innerHTML = `
                    <h2>${article.title}</h2>
                    <p><strong>Source:</strong> ${article.source} | <strong>Author:</strong> ${article.author}</p>
                    <p><strong>Published:</strong> ${article.publishedAt}</p>
                    <img src="${article.urlToImage}" alt="News Image" class="news-image small-news-image">
                    <p><a href="${article.url}" target="_blank">Read Full Article</a></p>
                `;

                newsContainer.appendChild(newsCard);
                setTimeout(() => newsCard.style.opacity = "1", 200); // Fade in effect
            });

            page++; // Move to next page
            loading = false;
        }
    }

    window.addEventListener("scroll", function () {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
            loadMoreNews();
        }

        // Show or hide back to top button
        if (window.scrollY > 300) {
            backToTopBtn.style.display = "block";
        } else {
            backToTopBtn.style.display = "none";
        }
    });

});
