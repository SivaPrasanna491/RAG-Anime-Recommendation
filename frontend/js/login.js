// API Base URL - Update this to match your backend
const API_BASE_URL = 'http://localhost:8000';

// Get form elements
const loginForm = document.getElementById('loginForm');
const submitBtn = document.getElementById('submitBtn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');

// Check for auth message from redirect
window.addEventListener('DOMContentLoaded', () => {
    const authMessage = localStorage.getItem('authMessage');
    if (authMessage) {
        showNotification(authMessage);
        localStorage.removeItem('authMessage');
    }
});

// Show notification
function showNotification(message) {
    const notificationBox = document.getElementById('notificationBox');
    const notificationText = document.getElementById('notificationText');
    const notificationClose = document.getElementById('notificationClose');
    
    notificationText.textContent = message;
    notificationBox.style.display = 'flex';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        notificationBox.style.display = 'none';
    }, 5000);
    
    // Close button
    notificationClose.addEventListener('click', () => {
        notificationBox.style.display = 'none';
    });
}

// Handle form submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Clear previous messages
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
    
    // Get form data
    const formData = new FormData(loginForm);
    const data = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    // Show loading state
    setLoading(true);
    
    try {
        // Make API request to login endpoint
        const response = await fetch(`${API_BASE_URL}/api/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            credentials: 'include' // Include cookies
        });
        
        const result = await response.json();
        
        // Check message and redirect accordingly
        if (result.message === 'Email not found. Please register') {
            // User not registered, redirect to signup
            localStorage.setItem('authMessage', 'Please first signup');
            window.location.href = 'signup';
            return;
        }
        
        if (response.ok && result.message === 'Login successful') {
            // Success
            showSuccess('Login successful! Redirecting...');
            
            // Save remember me preference
            if (formData.get('remember')) {
                localStorage.setItem('rememberMe', 'true');
                localStorage.setItem('userEmail', data.email);
            }
            
            // Redirect to home after 1.5 seconds
            setTimeout(() => {
                window.location.href = 'home';
            }, 1000);
        } else {
            // Other errors from server
            showError(result.detail || result.message || 'Login failed. Please check your credentials.');
        }
    } catch (error) {
        console.error('Login error:', error);
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

// Show success message
function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    successMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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

// Add input validation feedback
const inputs = loginForm.querySelectorAll('.form-input');
inputs.forEach(input => {
    input.addEventListener('blur', function() {
        if (this.value.trim() === '' && this.hasAttribute('required')) {
            this.style.borderColor = '#ef4444';
        } else {
            this.style.borderColor = '';
        }
    });
    
    input.addEventListener('focus', function() {
        this.style.borderColor = '';
        errorMessage.style.display = 'none';
    });
});

// Load remembered email if exists
window.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('rememberMe') === 'true') {
        const savedEmail = localStorage.getItem('userEmail');
        if (savedEmail) {
            document.getElementById('email').value = savedEmail;
            document.querySelector('input[name="remember"]').checked = true;
        }
    }
});

// Console message
console.log('%c🎌 AnimeAI Login ', 'background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; font-size: 16px; padding: 8px; border-radius: 4px;');
console.log('%cAPI Endpoint: ' + API_BASE_URL + '/api/users/login', 'color: #8b5cf6; font-size: 12px;');
