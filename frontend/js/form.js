// API Base URL
const API_BASE_URL = 'http://localhost:8000';

// Get form elements
const animeForm = document.getElementById('animeForm');
const submitBtn = document.getElementById('submitBtn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');
const errorMessage = document.getElementById('errorMessage');

// Get chip containers
const genreChips = document.getElementById('genreChips');
const themeChips = document.getElementById('themeChips');
const genreCount = document.getElementById('genreCount');
const themeCount = document.getElementById('themeCount');

// Selected values
let selectedGenres = [];
let selectedThemes = [];

// ===== GENRE CHIP SELECTION =====
genreChips.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', function() {
        const value = this.getAttribute('data-value');
        
        if (this.classList.contains('selected')) {
            // Deselect
            this.classList.remove('selected');
            selectedGenres = selectedGenres.filter(g => g !== value);
        } else {
            // Select
            this.classList.add('selected');
            if (!selectedGenres.includes(value)) {
                selectedGenres.push(value);
            }
        }
        
        updateGenreCount();
    });
});

function updateGenreCount() {
    genreCount.textContent = `${selectedGenres.length} selected`;
}

// ===== THEME CHIP SELECTION =====
themeChips.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', function() {
        const value = this.getAttribute('data-value');
        
        if (this.classList.contains('selected')) {
            // Deselect
            this.classList.remove('selected');
            selectedThemes = selectedThemes.filter(t => t !== value);
        } else {
            // Select
            this.classList.add('selected');
            if (!selectedThemes.includes(value)) {
                selectedThemes.push(value);
            }
        }
        
        updateThemeCount();
    });
});

function updateThemeCount() {
    themeCount.textContent = `${selectedThemes.length} selected`;
}

// ===== FORM SUBMISSION =====
animeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Clear previous messages
    errorMessage.style.display = 'none';
    
    // Get form data
    const title = document.getElementById('title').value.trim();
    const episodes = document.getElementById('episodes').value;
    
    // Build query string
    let queryParts = [];
    
    if (title) {
        queryParts.push(`anime with title "${title}"`);
    }
    
    if (selectedGenres.length > 0) {
        queryParts.push(`genres: ${selectedGenres.join(', ')}`);
    }
    
    if (selectedThemes.length > 0) {
        queryParts.push(`themes: ${selectedThemes.join(', ')}`);
    }
    
    if (episodes) {
        queryParts.push(`${episodes} episodes`);
    }
    
    // Create natural language query
    const query = queryParts.length > 0 
        ? `I want ${queryParts.join(' with ')}`
        : 'Recommend me some good anime';
    
    console.log('Query:', query);
    console.log('Selected Genres:', selectedGenres);
    console.log('Selected Themes:', selectedThemes);
    
    // Show loading state
    setLoading(true);
    
    try {
        // Make API request to recommendation endpoint
        const response = await fetch(`${API_BASE_URL}/api/anime/recommendation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
            credentials: 'include'
        });
        
        const result = await response.json();
        
        // Check if user is not authenticated
        if (result.message === 'User not authenticated') {
            // Store message and redirect to signup
            localStorage.setItem('authMessage', 'Please first signup');
            window.location.href = 'signup';
            return;
        }
        
        if (response.ok) {
            // Success - store results and redirect to results page
            console.log('Recommendations received:', result);
            localStorage.setItem('animeRecommendations', JSON.stringify(result));
            window.location.href = 'results';
        } else {
            // Error from server
            showError(result.detail || result.message || 'Failed to get recommendations. Please try again.');
        }
    } catch (error) {
        console.error('Recommendation error:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        setLoading(false);
    }
});

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Set loading state
function setLoading(isLoading) {
    if (isLoading) {
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
    } else {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
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
console.log('%c🎌 AnimeAI Search Form ', 'background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; font-size: 16px; padding: 8px; border-radius: 4px;');
console.log('%cAPI Endpoint: ' + API_BASE_URL + '/api/anime/recommendation', 'color: #8b5cf6; font-size: 12px;');
console.log('%cClick chips to select genres and themes!', 'color: #6366f1; font-size: 12px;');
