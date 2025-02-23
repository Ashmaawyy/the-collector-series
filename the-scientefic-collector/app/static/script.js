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
            fetch(`/search_papers?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    const papersContainer = document.getElementById("papers-container");
                    papersContainer.innerHTML = "";

                    data.papers.forEach(paper => {
                        const paperCard = document.createElement("div");
                        paperCard.classList.add("paper-card", "small-paper");
                        paperCard.innerHTML = `
                            ${paper.image_url ? `<img src="${paper.image_url}" alt="${paper.title}" class="paper-image">` : ""}
                            <h2>${paper.title}</h2>
                            <p><strong>Author:</strong> ${paper.author}</p>
                            <p><strong>Published:</strong> ${paper.publishedAt}</p>
                            <p><strong>Journal:</strong> ${paper.journal}</p>
                            <div class="paper-abstract">${paper.abstract}</div>
                            <a href="${paper.url}" target="_blank">Read Full Paper</a>
                        `;
                        papersContainer.appendChild(paperCard);
                    });
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

    async function loadMorePapers() {
        if (loading) return;
        loading = true;

        const response = await fetch(`/load_more_papers?page=${page}`);
        const data = await response.json();

        if (data.papers.length > 0) {
            const papersContainer = document.getElementById("papers-container");
            data.papers.forEach(paper => {
                const paperCard = document.createElement("div");
                paperCard.classList.add("paper-card", "small-paper");
                paperCard.style.opacity = "0";

                paperCard.innerHTML = `
                    <h2>${paper.title}</h2>
                    <p><strong>Author:</strong> ${paper.author}</p>
                    <p><strong>Published:</strong> ${paper.publishedAt}</p>
                    <p><strong>Journal:</strong> ${paper.journal}</p>
                    <a href=${paper.url } target="_blank">Read Full Paper</a>
                `;

                papersContainer.appendChild(paperCard);
                setTimeout(() => paperCard.style.opacity = "1", 200);
            });

            page++;
            loading = false;
        }
    }

    window.addEventListener("scroll", function () {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
            loadMorePapers();
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

    // Initial load
    loadMorePapers();
});
