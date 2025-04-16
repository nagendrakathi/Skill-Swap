document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips everywhere
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Enable popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Add hover effect to skill cards
    const skillCards = document.querySelectorAll('.skill-card');
    skillCards.forEach(card => {
        card.classList.add('card-hover');
    });

    // Handle skill filter dropdown selections
    const categoryFilters = document.querySelectorAll('.category-filter');
    categoryFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            const category = this.getAttribute('data-category');
            const currentUrl = new URL(window.location);
            
            if (category) {
                currentUrl.searchParams.set('category', category);
            } else {
                currentUrl.searchParams.delete('category');
            }
            
            window.location = currentUrl.toString();
        });
    });

    // Handle search form
    const searchForm = document.getElementById('skillSearchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('searchQuery');
            if (!searchInput.value.trim()) {
                e.preventDefault();
            }
        });
    }

    // Handle skill delete confirmation
    const deleteButtons = document.querySelectorAll('.delete-skill-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this skill? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Handle request accept/reject confirmation
    const actionButtons = document.querySelectorAll('.request-action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const action = this.getAttribute('data-action');
            const message = action === 'accept' 
                ? 'Are you sure you want to accept this request?' 
                : 'Are you sure you want to reject this request?';
            
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Auto-resize message textarea
    const messageTextarea = document.getElementById('content');
    if (messageTextarea) {
        messageTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        // Initial trigger for loaded content
        messageTextarea.dispatchEvent(new Event('input'));
    }

    // Scroll to bottom of message container
    const messageContainer = document.querySelector('.message-container');
    if (messageContainer) {
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    // Star rating functionality
    const ratingInputs = document.querySelectorAll('input[name="rating"]');
    const ratingDisplay = document.getElementById('ratingDisplay');
    
    if (ratingInputs.length && ratingDisplay) {
        ratingInputs.forEach(input => {
            input.addEventListener('change', function() {
                updateRatingStars(this.value);
            });
        });

        function updateRatingStars(rating) {
            ratingDisplay.innerHTML = '';
            for (let i = 1; i <= 5; i++) {
                const starIcon = document.createElement('i');
                starIcon.classList.add('fas', i <= rating ? 'fa-star' : 'fa-star-o');
                ratingDisplay.appendChild(starIcon);
            }
        }
    }
});