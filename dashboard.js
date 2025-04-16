// Dashboard JavaScript

// Variables
const sidebar = document.getElementById('sidebar');
const toggleSidebarBtn = document.getElementById('toggleSidebar');
const toggleThemeBtn = document.getElementById('toggleTheme');
const mainContent = document.querySelector('.main');
const body = document.body;

// Toggle sidebar
toggleSidebarBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
});

// Toggle theme (light/dark)
toggleThemeBtn.addEventListener('click', () => {
    body.classList.toggle('light-theme');
    
    // Update theme icon
    const themeIcon = toggleThemeBtn.querySelector('i');
    if (body.classList.contains('light-theme')) {
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
    } else {
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
    }
    
    // Save theme preference to localStorage
    const isDarkTheme = !body.classList.contains('light-theme');
    localStorage.setItem('darkTheme', isDarkTheme.toString());
});

// Check stored theme preference
document.addEventListener('DOMContentLoaded', () => {
    const storedDarkTheme = localStorage.getItem('darkTheme');
    
    // Apply stored theme if exists
    if (storedDarkTheme !== null) {
        const isDarkTheme = storedDarkTheme === 'true';
        
        if (!isDarkTheme) {
            body.classList.add('light-theme');
            const themeIcon = toggleThemeBtn.querySelector('i');
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    }
    
    // Show page after theme is applied (prevents flash)
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 50);
});

// Handle responsive behavior
function handleResponsive() {
    if (window.innerWidth < 992) {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
    } else {
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('expanded');
    }
}

// Initialize responsive behavior
handleResponsive();

// Re-check on window resize
window.addEventListener('resize', handleResponsive);

// Avatar edit button hover effect
const userAvatar = document.querySelector('.user-avatar');
const avatarEditBtn = document.querySelector('.avatar-edit-button');

if (userAvatar && avatarEditBtn) {
    userAvatar.addEventListener('mouseenter', () => {
        avatarEditBtn.style.opacity = '1';
        avatarEditBtn.style.transform = 'scale(1)';
    });
    
    userAvatar.addEventListener('mouseleave', () => {
        avatarEditBtn.style.opacity = '0';
        avatarEditBtn.style.transform = 'scale(0.9)';
    });
}

// Add notification badge functionality
const notificationBadges = document.querySelectorAll('.badge');
notificationBadges.forEach(badge => {
    if (parseInt(badge.textContent) === 0) {
        badge.style.display = 'none';
    }
});

// Smooth scroll for sidebar navigation
const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
sidebarLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        // If this is an anchor link
        if (this.getAttribute('href').startsWith('#')) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                // Remove active class from all links
                sidebarLinks.forEach(sLink => sLink.classList.remove('active'));
                
                // Add active class to clicked link
                this.classList.add('active');
                
                // Smooth scroll to target
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // If on mobile, collapse sidebar after clicking
                if (window.innerWidth < 992) {
                    sidebar.classList.add('collapsed');
                    mainContent.classList.add('expanded');
                }
            }
        }
    });
});