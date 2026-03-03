/**
 * Mobile Navigation Logic for Fajr Today
 */
function initNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navContainer = document.querySelector('.nav-container');
    const navLinks = document.querySelectorAll('nav ul li a');

    if (!navToggle || !navContainer) return;

    navToggle.addEventListener('click', () => {
        navContainer.classList.toggle('active');
        // Toggle hamburger animation state if needed
    });

    // Close menu when a link is clicked
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navContainer.classList.remove('active');
        });
    });

    // Close on click outside
    document.addEventListener('click', (e) => {
        if (!navContainer.contains(e.target) && !navToggle.contains(e.target) && navContainer.classList.contains('active')) {
            navContainer.classList.remove('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', initNavigation);
