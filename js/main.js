/**
 * Main JavaScript file for DzTeck Forum - XenForo Style
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggler enhancement
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    }

    // File input enhancement for avatar upload
    const fileInput = document.getElementById('avatar');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            // Show file name if selected
            const fileName = this.files[0]?.name;
            if (fileName) {
                // Display the file name near the input
                const fileNameLabel = document.querySelector('.file-name');
                if (fileNameLabel) {
                    fileNameLabel.textContent = fileName;
                    fileNameLabel.classList.remove('d-none');
                } else {
                    // Create a label if it doesn't exist
                    const label = document.createElement('div');
                    label.className = 'file-name form-text mt-1';
                    label.textContent = fileName;
                    fileInput.parentNode.appendChild(label);
                }
            }
        });
    }

    // Enhance reaction buttons
    const reactionButtons = document.querySelectorAll('.reaction-btn');
    reactionButtons.forEach(button => {
        // Add hover effect
        button.addEventListener('mouseover', function() {
            this.classList.add('pulse');
        });
        
        button.addEventListener('mouseout', function() {
            this.classList.remove('pulse');
        });
        
        // Add active class when clicked (only for visual feedback, actual toggling is handled by the server)
        button.addEventListener('click', function() {
            const parentForm = this.closest('form');
            if (parentForm) {
                // Add loading state
                this.classList.add('loading');
                
                // Submit the form (the server will handle the actual reaction)
                parentForm.submit();
            }
        });
    });

    // Auto-resize textarea for better UX
    document.querySelectorAll('textarea.form-control').forEach(textarea => {
        textarea.addEventListener('input', function() {
            // Reset height first to get the correct scrollHeight
            this.style.height = 'auto';
            // Set the height to match content (+2px to prevent scrollbar flickering)
            this.style.height = (this.scrollHeight + 2) + 'px';
        });
        
        // Initial resize
        if (textarea.value) {
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight + 2) + 'px';
        }
    });

    // Handle thread reply button
    const replyButtons = document.querySelectorAll('.btn-reply');
    replyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the thread ID from the container
            const threadDetail = this.closest('.thread-detail');
            if (threadDetail) {
                const threadId = threadDetail.id.replace('thread-', '');
                
                // Create reply form if not exists
                let replyForm = document.getElementById('reply-form-' + threadId);
                if (!replyForm) {
                    replyForm = document.createElement('div');
                    replyForm.id = 'reply-form-' + threadId;
                    replyForm.className = 'reply-form mt-4';
                    replyForm.innerHTML = `
                        <h5 class="mb-3">إضافة رد</h5>
                        <form action="#" method="post">
                            <input type="hidden" name="csrf_token" value="">
                            <input type="hidden" name="thread_id" value="${threadId}">
                            <div class="mb-3">
                                <textarea class="form-control" name="content" rows="4" placeholder="أكتب ردك هنا..." required></textarea>
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary btn-cancel-reply me-2">إلغاء</button>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-paper-plane me-1"></i> إرسال الرد
                                </button>
                            </div>
                        </form>
                    `;
                    
                    // Insert after the reply button
                    const replyAction = this.closest('.reply-action');
                    replyAction.after(replyForm);
                    
                    // Set CSRF token
                    const csrfToken = document.querySelector('input[name="csrf_token"]').value;
                    replyForm.querySelector('input[name="csrf_token"]').value = csrfToken;
                    
                    // Add cancel button handler
                    replyForm.querySelector('.btn-cancel-reply').addEventListener('click', function() {
                        replyForm.remove();
                    });
                    
                    // Focus the textarea
                    replyForm.querySelector('textarea').focus();
                } else {
                    // Toggle existing form
                    replyForm.remove();
                }
            }
        });
    });

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Only process if it's an actual anchor (not just "#")
            if (href !== '#') {
                e.preventDefault();
                const targetElement = document.querySelector(href);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Check if we need to scroll to a specific thread (for redirects after posting)
    const hash = window.location.hash;
    if (hash && hash.startsWith('#thread-')) {
        const threadElement = document.querySelector(hash);
        if (threadElement) {
            // Slight delay to ensure DOM is fully loaded
            setTimeout(() => {
                threadElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                // Add a highlight effect
                threadElement.classList.add('highlight');
                setTimeout(() => {
                    threadElement.classList.remove('highlight');
                }, 2000);
            }, 300);
        }
    }
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Add a simple confirmation for logout
const logoutBtn = document.querySelector('a[href*="logout"]');
if (logoutBtn) {
    logoutBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (confirm('هل أنت متأكد من تسجيل الخروج؟')) {
            window.location.href = this.href;
        }
    });
}
