// Main JavaScript for GymStore

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation and button handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const password1 = form.querySelector('input[name="password1"]');
            const password2 = form.querySelector('input[name="password2"]');
            const submitButton = form.querySelector('button[type="submit"]');
            
            // Store original button content
            const originalButtonContent = submitButton.innerHTML;
            
            // Add loading state
            if (submitButton) {
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitButton.disabled = true;
            }
            
            // Password validation
            if (password1 && password2) {
                if (password1.value !== password2.value) {
                    e.preventDefault();
                    alert('Passwords do not match!');
                    
                    // Reset button
                    if (submitButton) {
                        submitButton.innerHTML = originalButtonContent;
                        submitButton.disabled = false;
                    }
                    return false;
                }
            }
            
            // If form validation passes, let it submit
            // The button will reset when page reloads
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                alert.classList.remove('show');
                alert.classList.add('fade');
            }
        }, 5000);
    });
});