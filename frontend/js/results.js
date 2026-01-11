// API Base URL
const API_BASE_URL = 'http://localhost:8000';

// Get elements
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const resultsGrid = document.getElementById('resultsGrid');
const backButton = document.getElementById('backButton');

// Load recommendations on page load
document.addEventListener('DOMContentLoaded', () => {
    loadRecommendations();
});

// Load recommendations from localStorage
function loadRecommendations() {
    try {
        // Get recommendations from localStorage (set by form.js)
        const recommendationsData = localStorage.getItem('animeRecommendations');
        
        if (!recommendationsData) {
            showError('No recommendations found. Please search for anime first.');
            return;
        }
        
        const recommendations = JSON.parse(recommendationsData);
        console.log('Loaded recommendations:', recommendations);
        
        // Hide loading, show results
        loadingState.style.display = 'none';
        resultsGrid.style.display = 'grid';
        backButton.style.display = 'block';
        
        // Display recommendations
        displayRecommendations(recommendations);
        
        // Clear localStorage after displaying
        // localStorage.removeItem('animeRecommendations');
        
    } catch (error) {
        console.error('Error loading recommendations:', error);
        showError('Failed to load recommendations. Please try again.');
    }
}

// Display recommendations as cards
function displayRecommendations(recommendations) {
    resultsGrid.innerHTML = '';
    
    if (!recommendations || recommendations.length === 0) {
        showError('No anime recommendations found. Try a different search!');
        return;
    }
    
    recommendations.forEach((anime, index) => {
        const card = createAnimeCard(anime, index);
        resultsGrid.appendChild(card);
    });
}

// Create anime card element
function createAnimeCard(anime, index) {
    const card = document.createElement('div');
    card.className = 'anime-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    card.innerHTML = `
        <div class="anime-image">
            <img src="${anime.url || 'https://via.placeholder.com/320x400?text=No+Image'}" 
                 alt="${anime.title}"
                 onerror="this.src='https://via.placeholder.com/320x400?text=No+Image'">
        </div>
        <div class="anime-content">
            <h3 class="anime-title">${anime.title}</h3>
            <p class="anime-genre">${anime.genre}</p>
            <p class="anime-reason">${anime.reason}</p>
        </div>
    `;
    
    // Add click event to view anime details (optional)
    card.addEventListener('click', () => {
        console.log('Clicked anime:', anime);
        // You can add navigation to anime details page here
        // window.location.href = `anime-details?title=${encodeURIComponent(anime.title)}`;
    });
    
    return card;
}

// Show error state
function showError(message) {
    loadingState.style.display = 'none';
    resultsGrid.style.display = 'none';
    errorState.style.display = 'block';
    errorMessage.textContent = message;
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

// Console message
console.log('%c🎌 AnimeAI Results ', 'background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; font-size: 16px; padding: 8px; border-radius: 4px;');
console.log('%cDisplaying your personalized anime recommendations!', 'color: #8b5cf6; font-size: 12px;');
