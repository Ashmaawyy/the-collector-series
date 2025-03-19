document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById('theme-toggle');
    const searchInput = document.getElementById('search-input');
    const papersContainer = document.getElementById('papers-container');
    let isLoading = false;
    let currentPage = 1;
    let hasMore = true;

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
        const card = document.createElement('div');
        card.className = 'paper-card';
        card.innerHTML = `
            <div class="paper-header">
                <h2>${paper.title || 'Untitled Paper'}</h2>
            </div>
            <div class="paper-meta">
                <span><i class="fas fa-user"></i> ${paper.author || 'Author not available'}</span>
                <span><i class="fas fa-calendar"></i> ${paper.publishedAt || 'Date not available'}</span>
                <span><i class="fas fa-book"></i> ${paper.journal || 'Unknown Journal'}</span>
            </div>
            <div class="abstract-toggle">
                <i class="fas fa-chevron-down"></i>
                <span>Abstract</span>
            </div>
            <div class="paper-abstract">
                <p>${paper.abstract.p}</p>
            </div>
            <div class="paper-footer">
                <a href="${paper.url || '#'}" target="_blank" class="paper-link">
                    Read Full Paper <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
        `;
        return card;
    };

    const appendPapers = (papers) => {
        papers.forEach(paper => {
            const card = createPaperCard(paper);
            papersContainer.appendChild(card);
            fadeInElement(card);

            // Add event listener for abstract toggle
            const toggle = card.querySelector('.abstract-toggle');
            toggle.addEventListener('click', () => {
                const abstract = card.querySelector('.paper-abstract');
                abstract.classList.toggle('active');
                toggle.querySelector('i').classList.toggle('fa-chevron-up');
            });
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
