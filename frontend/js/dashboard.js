// API Base URL
const API_BASE_URL = 'http://localhost:8000';

// Get elements
const emptyState = document.getElementById('emptyState');
const animeGrid = document.getElementById('animeGrid');

// Check if user is logged in
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/home`, {
            method: 'GET',
            credentials: 'include'
        });
        
        const result = await response.json();
        
        // Check if user is not authenticated
        if (result.message === 'User not authenticated' || result.message === 'User not signed up') {
            // Store message for signup page
            localStorage.setItem('authMessage', 'Please first signup');
            window.location.href = 'signup';
            return false;
        }
        
        if (!response.ok) {
            // Other errors, redirect to login
            localStorage.setItem('authMessage', 'Please login to continue');
            window.location.href = 'login';
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Auth check error:', error);
        // On error, redirect to signup
        localStorage.setItem('authMessage', 'Please first signup');
        window.location.href = 'signup';
        return false;
    }
}

// Load user's anime from database
async function loadUserAnime() {
    try {
        // TODO: Replace with actual API endpoint to fetch user's watched anime
        // For now, we'll check localStorage or return empty
        const storedAnime = localStorage.getItem('userAnime');
        
        if (storedAnime) {
            const animeList = JSON.parse(storedAnime);
            if (animeList && animeList.length > 0) {
                displayAnimeGrid(animeList);
                return;
            }
        }
        
        // No anime found, show empty state
        showEmptyState();
    } catch (error) {
        console.error('Error loading anime:', error);
        showEmptyState();
    }
}

// Show empty state
function showEmptyState() {
    emptyState.style.display = 'flex';
    animeGrid.style.display = 'none';
}

// Display anime grid
function displayAnimeGrid(animeList) {
    emptyState.style.display = 'none';
    animeGrid.style.display = 'grid';
    
    // Clear existing content
    animeGrid.innerHTML = '';
    
    // Create anime cards
    animeList.forEach(anime => {
        const card = createAnimeCard(anime);
        animeGrid.appendChild(card);
    });
}

// Create anime card element
function createAnimeCard(anime) {
    const card = document.createElement('div');
    card.className = 'anime-card';
    
    card.innerHTML = `
        <div class="anime-image">
            ${anime.image ? `<img src="${anime.image}" alt="${anime.title}">` : '🎬'}
        </div>
        <h3 class="anime-title">${anime.title}</h3>
        <p class="anime-genre">${anime.genre || 'Unknown Genre'}</p>
        <p class="anime-description">${anime.description || anime.reason || 'No description available.'}</p>
        ${anime.tags ? `
            <div class="anime-tags">
                ${anime.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
        ` : ''}
    `;
    
    // Add click handler
    card.addEventListener('click', () => {
        // TODO: Navigate to anime details page
        console.log('Clicked anime:', anime.title);
    });
    
    return card;
}

// Logout functionality
document.querySelector('.btn-logout').addEventListener('click', async () => {
    try {
        await fetch(`${API_BASE_URL}/api/users/logout`, {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        localStorage.clear();
        window.location.href = 'index';
    }
});

// Initialize dashboard
async function init() {
    // Check authentication
    const isAuthenticated = await checkAuth();
    
    if (isAuthenticated) {
        // Load user's anime
        await loadUserAnime();
    }
}

// Run on page load
init();

// Console message
console.log('%c🎌 AnimeAI Dashboard ', 'background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; font-size: 16px; padding: 8px; border-radius: 4px;');
console.log('%cWelcome to your anime dashboard!', 'color: #8b5cf6; font-size: 12px;');
