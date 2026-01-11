// API Base URL - Update this to match your backend
const API_BASE_URL = 'http://localhost:8000';

// Get form elements
const signupForm = document.getElementById('signupForm');
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
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Clear previous messages
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
    
    // Get form data
    const formData = new FormData(signupForm);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        password: formData.get('password'),
        gender: formData.get('gender')
    };
    
    // Validate password length
    if (data.password.length < 8) {
        showError('Password must be at least 8 characters long');
        return;
    }
    
    // Show loading state
    setLoading(true);
    
    try {
        // Make API request to signup endpoint
        const response = await fetch(`${API_BASE_URL}/api/users/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            credentials: 'include' // Include cookies
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Signup successful - redirect to home
            showSuccess('Account created successfully! Redirecting...');
            
            // Redirect to home after 2 seconds
            setTimeout(() => {
                window.location.href = 'home';
            }, 1000);
        } else {
            // Error from server
            showError(result.detail || result.message || 'Signup failed. Please try again.');
        }
    } catch (error) {
        console.error('Signup error:', error);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
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
const inputs = signupForm.querySelectorAll('.form-input');
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

// Real-time password validation
const passwordInput = document.getElementById('password');
passwordInput.addEventListener('input', function() {
    const hint = this.nextElementSibling;
    if (this.value.length > 0 && this.value.length < 8) {
        hint.style.color = '#ef4444';
        hint.textContent = `${8 - this.value.length} more characters needed`;
    } else if (this.value.length >= 8) {
        hint.style.color = '#22c55e';
        hint.textContent = 'Strong password ✓';
    } else {
        hint.style.color = '';
        hint.textContent = 'Must be at least 8 characters';
    }
});

// Console message
console.log('%c🎌 AnimeAI Signup ', 'background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; font-size: 16px; padding: 8px; border-radius: 4px;');
console.log('%cAPI Endpoint: ' + API_BASE_URL + '/api/users/signup', 'color: #8b5cf6; font-size: 12px;');
