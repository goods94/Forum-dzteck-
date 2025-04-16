/**
 * Facebook-style Reactions for DzTeck Forum
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize reactions system
    initReactions();

    // When AJAX loads new content, reinitialize
    document.addEventListener('content-loaded', function() {
        initReactions();
    });

    function initReactions() {
        const reactionButtons = document.querySelectorAll('.reaction-btn');

        reactionButtons.forEach(btn => {
            // Add data attributes for reactions
            const reactionType = getReactionType(btn);
            if (reactionType) {
                btn.setAttribute('data-reaction', reactionType);
            }

            // Remove existing event listeners (to prevent duplicates)
            btn.removeEventListener('click', handleReactionClick);
            
            // Add click event listener
            btn.addEventListener('click', handleReactionClick);

            // Add hover effect with emojis
            setupReactionHoverEffect(btn);
        });
    }

    function getReactionType(btn) {
        // Extract reaction type from classes or HTML content
        if (btn.querySelector('.fa-thumbs-up')) return 'like';
        if (btn.querySelector('.fa-heart')) return 'love';
        if (btn.querySelector('.fa-laugh')) return 'laugh';
        if (btn.querySelector('.fa-sad-tear')) return 'sad';
        if (btn.querySelector('.fa-angry')) return 'angry';
        return null;
    }

    function handleReactionClick(e) {
        // Prevent default form submission
        e.preventDefault();
        
        const btn = this;
        const form = btn.closest('form');
        
        if (!form) return; // Safety check
        
        // Add animation class
        btn.classList.add('pop');
        
        // Remove animation class after animation completes
        setTimeout(() => {
            btn.classList.remove('pop');
        }, 300);

        // Add loading ripple effect
        btn.classList.add('loading');
        
        // Simulate reaction change immediately for better UX
        simulateReactionChange(btn);
        
        // Get form data
        const formData = new FormData(form);
        
        // Send AJAX request instead of regular form submission
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading state
            btn.classList.remove('loading');
            
            if (data.success) {
                // Update reaction buttons based on server response
                updateReactionUI(data.thread_id, data.emoji, data.reaction_counts, data.user_reacted, data.current_reaction);
            } else {
                console.error('Error processing reaction:', data.error);
            }
        })
        .catch(error => {
            console.error('Error processing reaction:', error);
            btn.classList.remove('loading');
        });
    }
    
    // Update UI based on reaction response
    function updateReactionUI(threadId, emoji, counts, userReacted, currentReaction) {
        // Select all reaction buttons for this thread
        const threadForms = document.querySelectorAll(`form.reaction-form input[name="thread_id"][value="${threadId}"]`);
        
        threadForms.forEach(input => {
            const form = input.closest('form');
            const emojiInput = form.querySelector('input[name="emoji"]');
            const emojiType = emojiInput.value;
            const button = form.querySelector('.reaction-btn');
            
            // Update count display
            const countSpan = button.querySelector('.count');
            const newCount = counts[emojiType] || 0;
            
            if (newCount > 0) {
                if (countSpan) {
                    countSpan.textContent = newCount;
                } else {
                    const newCountSpan = document.createElement('span');
                    newCountSpan.className = 'count';
                    newCountSpan.textContent = newCount;
                    button.appendChild(newCountSpan);
                }
            } else if (countSpan) {
                countSpan.remove();
            }
            
            // Update active state
            if (emojiType === currentReaction) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
            
            // Update icon color
            const icon = button.querySelector('i');
            if (emojiType === currentReaction) {
                icon.className = icon.className.replace(/\b\w+-color\b/g, '');
            } else {
                if (!icon.className.includes(`${emojiType}-color`)) {
                    icon.className = icon.className.replace(/\b\w+-color\b/g, '');
                    icon.className += ` ${emojiType}-color`;
                }
            }
        });
    }

    function simulateReactionChange(btn) {
        const reactionType = btn.getAttribute('data-reaction');
        const isActive = btn.classList.contains('active');
        
        // Toggle active state for visual feedback
        if (isActive) {
            btn.classList.remove('active');
        } else {
            btn.classList.add('active');
            
            // Add shake animation for fun
            btn.querySelector('i').classList.add('pop');
            setTimeout(() => {
                btn.querySelector('i').classList.remove('pop');
            }, 300);
        }
    }

    function setupReactionHoverEffect(btn) {
        // Get existing reaction container or create new one
        let reactionsContainer = btn.previousElementSibling;
        if (!reactionsContainer || !reactionsContainer.classList.contains('facebook-reactions')) {
            // Create reactions hover container if it doesn't exist
            const form = btn.closest('form');
            if (!form) return; // Safety check
            
            reactionsContainer = document.createElement('div');
            reactionsContainer.className = 'facebook-reactions';
            
            // Add the reaction buttons - like, love, laugh, sad, angry
            reactionsContainer.innerHTML = `
                <button type="button" class="facebook-reaction-btn" data-reaction="like" title="أعجبني">
                    <i class="fas fa-thumbs-up fa-lg like-color"></i>
                </button>
                <button type="button" class="facebook-reaction-btn" data-reaction="love" title="أحببته">
                    <i class="fas fa-heart fa-lg love-color"></i>
                </button>
                <button type="button" class="facebook-reaction-btn" data-reaction="laugh" title="مضحك">
                    <i class="fas fa-laugh fa-lg laugh-color"></i>
                </button>
                <button type="button" class="facebook-reaction-btn" data-reaction="sad" title="محزن">
                    <i class="fas fa-sad-tear fa-lg sad-color"></i>
                </button>
                <button type="button" class="facebook-reaction-btn" data-reaction="angry" title="أغضبني">
                    <i class="fas fa-angry fa-lg angry-color"></i>
                </button>
            `;
            
            // Insert before the button
            form.insertBefore(reactionsContainer, btn);
            
            // Handle reaction buttons
            const reactionBtns = reactionsContainer.querySelectorAll('.facebook-reaction-btn');
            reactionBtns.forEach(reactionBtn => {
                reactionBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Get the reaction type
                    const reaction = this.getAttribute('data-reaction');
                    
                    // Update hidden input with the reaction
                    const emojiInput = form.querySelector('input[name="emoji"]');
                    if (emojiInput) {
                        emojiInput.value = reaction;
                    }
                    
                    // Add animation and effect to reaction button
                    const button = form.querySelector('.reaction-btn');
                    button.classList.add('loading');
                    button.classList.add('pop');
                    
                    // Get form data
                    const formData = new FormData(form);
                    
                    // Send AJAX request
                    fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Remove loading state
                        button.classList.remove('loading');
                        
                        if (data.success) {
                            // Update reaction buttons based on server response
                            updateReactionUI(data.thread_id, data.emoji, data.reaction_counts, data.user_reacted, data.current_reaction);
                        } else {
                            console.error('Error processing reaction:', data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error processing reaction:', error);
                        button.classList.remove('loading');
                    });
                });
            });
        }
    }
});