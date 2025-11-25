/**
 * WaterBuddy Profile Page Functionality
 * Handles profile form validation and submission
 */

class ProfileManager {
    constructor(formId) {
        this.form = document.getElementById(formId);
        if (!this.form) return;
        
        this.setupEventListeners();
        this.setupFormValidation();
    }
    
    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.validateForm(e));
        
        // Input field validations
        const numberInputs = this.form.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.addEventListener('input', () => this.validateNumberInput(input));
        });
    }
    
    setupFormValidation() {
        // Add custom validation classes and feedback elements
        const requiredInputs = this.form.querySelectorAll('input[required]');
        requiredInputs.forEach(input => {
            // Create validation feedback element
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'text-red-500 text-sm mt-1 hidden';
            feedbackDiv.id = `${input.id}-feedback`;
            input.parentNode.appendChild(feedbackDiv);
            
            // Add blur event for validation
            input.addEventListener('blur', () => this.validateInput(input));
        });
    }
    
    validateInput(input) {
        const feedbackEl = document.getElementById(`${input.id}-feedback`);
        if (!feedbackEl) return;
        
        // Check if empty
        if (input.hasAttribute('required') && !input.value.trim()) {
            feedbackEl.textContent = 'This field is required';
            feedbackEl.classList.remove('hidden');
            input.classList.add('border-red-500');
            return false;
        }
        
        // Specific validations based on input type
        if (input.type === 'number') {
            return this.validateNumberInput(input);
        } else if (input.type === 'email' && input.value.trim()) {
            // Simple email validation if provided
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(input.value)) {
                feedbackEl.textContent = 'Please enter a valid email address';
                feedbackEl.classList.remove('hidden');
                input.classList.add('border-red-500');
                return false;
            }
        }
        
        // Valid input
        feedbackEl.classList.add('hidden');
        input.classList.remove('border-red-500');
        return true;
    }
    
    validateNumberInput(input) {
        const feedbackEl = document.getElementById(`${input.id}-feedback`);
        if (!feedbackEl) return true;
        
        const value = parseFloat(input.value);
        const min = parseFloat(input.getAttribute('min') || '-Infinity');
        const max = parseFloat(input.getAttribute('max') || 'Infinity');
        
        if (isNaN(value)) {
            feedbackEl.textContent = 'Please enter a valid number';
            feedbackEl.classList.remove('hidden');
            input.classList.add('border-red-500');
            return false;
        }
        
        if (value < min) {
            feedbackEl.textContent = `Value must be at least ${min}`;
            feedbackEl.classList.remove('hidden');
            input.classList.add('border-red-500');
            return false;
        }
        
        if (value > max) {
            feedbackEl.textContent = `Value must be at most ${max}`;
            feedbackEl.classList.remove('hidden');
            input.classList.add('border-red-500');
            return false;
        }
        
        feedbackEl.classList.add('hidden');
        input.classList.remove('border-red-500');
        return true;
    }
    
    validateForm(e) {
        let isValid = true;
        
        // Validate all required inputs
        const requiredInputs = this.form.querySelectorAll('input[required]');
        requiredInputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            
            // Scroll to first invalid input
            const firstInvalid = this.form.querySelector('input.border-red-500');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalid.focus();
            }
        }
    }
    
    // Helper method to show a notification
    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-4 py-3 rounded-lg shadow-lg z-50 ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white`;
        notification.innerHTML = message;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('opacity-0', 'transition-opacity', 'duration-500');
            setTimeout(() => notification.remove(), 500);
        }, 5000);
    }
}

// Initialize profile manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the profile page
    if (document.getElementById('profileForm')) {
        window.profileManager = new ProfileManager('profileForm');
    }
});