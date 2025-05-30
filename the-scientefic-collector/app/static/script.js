document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById('theme-toggle');
    const searchInput = document.getElementById('search-input');
    const papersContainer = document.getElementById('papers-container');
    let isLoading = false;
    let currentPage = 1;
    let hasMore = true;
    const seenTitles = new Set();

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

    const fetchPapers = async (page, query = '') => {
        try {
            isLoading = true;
            showLoadingIndicator();
            const response = await fetch(`/api/load-more-papers?page=${page}&q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error(response.statusText);
            const { papers, next_page } = await response.json();
            if (papers.length === 0) {
                hasMore = false;
                showMessage('No more papers to load');
                return [];
            }
            currentPage = next_page || currentPage + 1;
            hasMore = !!next_page;
            return papers;
        } catch (error) {
            hasMore = false;
            showMessage(`Error loading papers: ${error.message}`, 'error');
            return [];
        } finally {
            isLoading = false;
            hideLoadingIndicator();
        }
    };

    const createPaperCard = (paper) => {
        const card = document.createElement("div");
        card.classList.add("paper-card");

        const title = document.createElement("h2");
        title.innerHTML = `<i class="fas fa-book"></i> ${paper.title || "Untitled Paper"}`;

        const doi = document.createElement("p");
        doi.innerHTML = `<i class="fas fa-barcode"></i> <strong>DOI:</strong> ${paper.doi}`;
        doi.classList.add("doi-text");

        const authors = document.createElement("p");
        authors.innerHTML = `<i class="fas fa-user"></i> <strong>Authors:</strong> ${paper.authors ? paper.authors.join(", ") : "Unknown"}`;

        const journal = document.createElement("p");
        journal.innerHTML = `<i class="fas fa-newspaper"></i> <strong>Journal:</strong> ${paper.publisherName || "Not Available"}`;

        const publicationDate = document.createElement("p");
        publicationDate.innerHTML = `<i class="fas fa-calendar-alt"></i> <strong>Published:</strong> ${paper.publicationDate || "Unknown Date"}`;

        const toggleAbstract = document.createElement("div");
        toggleAbstract.classList.add("abstract-toggle");
        toggleAbstract.innerHTML = '<i class="fas fa-chevron-down"></i> <span>Abstract</span>';

        const abstract = document.createElement("p");
        abstract.innerHTML = `${paper.abstract.p || "No abstract available."}`;
        abstract.classList.add("paper-abstract");

        toggleAbstract.addEventListener("click", function () {
            abstract.classList.toggle("active");
            toggleAbstract.querySelector("i").classList.toggle("fa-chevron-up");
        });

        const readMore = document.createElement("a");
        readMore.href = paper.url || "#";
        readMore.innerHTML = '<i class="fas fa-external-link-alt"></i> Read Full Article';
        readMore.target = "_blank";
        readMore.classList.add("read-more-btn");

        card.appendChild(title);
        card.appendChild(doi);
        card.appendChild(authors);
        card.appendChild(journal);
        card.appendChild(publicationDate);
        card.appendChild(toggleAbstract);
        card.appendChild(abstract);
        card.appendChild(readMore);

        return card;
    };

    const getPaperTitle = (paper) => paper.title || "Untitled Paper";

    const appendPapers = (papers) => {
        papers.forEach(paper => {
            const title_text = getPaperTitle(paper);
            if (seenTitles.has(title_text)) return; // Skip duplicate papers
            seenTitles.add(title_text);
            const card = createPaperCard(paper);
            papersContainer.appendChild(card);
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
        loader.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading more papers...';
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

    const loadMorePapers = async () => {
        if (isLoading || !hasMore) return;
        const papers = await fetchPapers(currentPage, searchInput.value.trim());
        appendPapers(papers);
    };

    searchInput.addEventListener('input', debounce(async (e) => {
        currentPage = 1;
        hasMore = true;
        papersContainer.innerHTML = '';
        seenTitles.clear();
        const papers = await fetchPapers(currentPage, e.target.value);
        appendPapers(papers);
    }, 300));

    window.addEventListener('scroll', () => {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        if (!isLoading && hasMore && (scrollTop + clientHeight >= scrollHeight - 100)) {
            loadMorePapers();
        }
    });

    loadMorePapers();
});
