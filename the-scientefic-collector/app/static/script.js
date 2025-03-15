document.addEventListener("DOMContentLoaded", function () {
    // Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    const applyTheme = (theme) => {
      document.documentElement.classList.toggle('dark-mode', theme === 'dark');
      localStorage.setItem('theme', theme);
    };
    
    themeToggle.addEventListener('change', (e) => {
      applyTheme(e.target.checked ? 'dark' : 'light');
    });
    
    // Apply saved theme
    applyTheme(localStorage.getItem('theme') || 'light');
    
    loadMorePapers()

    // Collapsible Abstracts
    document.querySelectorAll('.abstract-toggle').forEach(toggle => {
      toggle.addEventListener('click', () => {
        const abstract = toggle.closest('.paper-card').querySelector('.paper-abstract');
        abstract.classList.toggle('active');
        toggle.querySelector('i').classList.toggle('fa-chevron-up');
      });
    });
  
    // Search with Debounce
    const searchInput = document.getElementById('search-input');
    const debounceSearch = debounce(async (query) => {
      try {
        const response = await fetch(`/search_papers?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        updatePapersContainer(data.papers);
      } catch (error) {
        showToast('Error searching papers', 'error');
      }
    }, 300);
  
    searchInput.addEventListener('input', (e) => debounceSearch(e.target.value));
  
    // Infinite Scroll
    let isLoading = false;
    let currentPage = 1;
    let hasMore = true;
    
    async function loadMorePapers() {
        if (isLoading || !hasMore) return;
        
        try {
            isLoading = true;
            showLoadingIndicator();

            const response = await fetch(
                `/api/load-more-papers?page=${currentPage}&q=${encodeURIComponent(searchInput.value.trim())}`
            );

            if (!response.ok) throw new Error(response.statusText);
            
            const { papers, next_page } = await response.json();
            
            if (papers.length === 0) {
                hasMore = false;
                showMessage('No more papers to load');
                return;
            }

            appendPapers(papers);
            currentPage = next_page || currentPage + 1;

        } catch (error) {
            hasMore = false;
            showMessage(`Error loading papers: ${error.message}`, 'error');
        } finally {
            isLoading = false;
            hideLoadingIndicator();
        }
    }

    window.addEventListener('scroll', () => {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        const threshold = 100;
        
        console.log(
            `Scroll Position: ${Math.round(scrollTop + clientHeight)}/${Math.round(scrollHeight - threshold)}`,
            `Trigger: ${scrollTop + clientHeight >= scrollHeight - threshold}`
        );
    
        if (!isLoading && hasMore && (scrollTop + clientHeight >= scrollHeight - threshold)) {
            console.log('--- Triggering paper load ---');
            loadMorePapers();
        }
    });
    
    function appendPapers(papers) {
        const container = document.getElementById('papers-container');
        if (!container) {
            console.error('Papers container element not found!');
            return;
        }
    
        if (papers.length === 0) {
            console.log('No papers to append');
            return;
        }
    
        papers.forEach(paper => {
            const card = createPaperCard(paper);
            if (card) {
                container.appendChild(card);
                fadeInElement(card);
                console.log('Appended paper:', paper.title); // Debug log
            }
        });
    }
    
        // 💡 Fixed paper card creation
    function createPaperCard(paper) {
        try {
            const card = document.createElement('div');
            card.className = 'paper-card';

            // 💡 Safely handle array fields
            const authors = Array.isArray(paper.authors) ? paper.authors : [paper.authors || 'Unknown Author'];
            const subjects = Array.isArray(paper.subjects) ? paper.subjects : [paper.subjects || 'Uncategorized'];

            card.innerHTML = `
                <div class="paper-header">
                    <h2>${paper.title || 'Untitled Paper'}</h2>
                    <div class="paper-actions">
                        <button class="icon-btn"><i class="far fa-bookmark"></i></button>
                        <button class="icon-btn"><i class="fas fa-share"></i></button>
                    </div>
                </div>
                <div class="paper-meta">
                    ${authors.map(a => `<span><i class="fas fa-user"></i> ${a}</span>`).join('')}
                    <span><i class="fas fa-calendar"></i> ${paper.publication_date || 'Date not available'}</span>
                    <span><i class="fas fa-book"></i> ${paper.journal || 'Unknown Journal'}</span>
                </div>
                <div class="paper-tags">
                    ${subjects.map(s => `<span class="tag">${s}</span>`).join('')}
                </div>
                <div class="paper-footer">
                    <a href="${paper.url || '#'}" target="_blank" class="paper-link">
                        Read Full Paper <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            `;
            return card;
        } catch (error) {
            console.error('Error creating paper card:', error);
            return document.createElement('div'); // Return empty div as fallback
        }
    }
  
    // Helper Functions
    function debounce(fn, delay) {
      let timeout;
      return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn(...args), delay);
      };
    }

    // 💡 Fixed fade-in animation
    function fadeInElement(element) {
        element.style.opacity = '0';
        element.style.display = 'block'; // Ensure element is visible
        requestAnimationFrame(() => {
            element.style.transition = 'opacity 0.3s ease-out';
            element.style.opacity = '1';
        });
    }
  
    function updatePapersContainer(papers) {
      const container = document.getElementById('papers-container');
      container.innerHTML = '';
      appendPapers(papers);
    }
  
    function showToast(message, type = 'info') {
      const toast = document.createElement('div');
      toast.className = `toast ${type}`;
      toast.textContent = message;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    }

    function showLoadingIndicator() {
        const loader = document.createElement('div');
        loader.id = 'loading-indicator';
        loader.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading more papers...';
        document.body.appendChild(loader);
    }

    function hideLoadingIndicator() {
        const loader = document.getElementById('loading-indicator');
        if (loader) loader.remove();
    }
  });
