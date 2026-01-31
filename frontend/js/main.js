window.addEventListener('DOMContentLoaded', () => {
    // Initialize Animate On Scroll (AOS)
    // This provides the automated visual effects the user requested
    AOS.init({
        duration: 1000,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });

    // Number Counter Animation
    // Emulates the "Impact" section counters on fidf.org
    const counters = document.querySelectorAll('.counter');
    const speed = 200; // The lower the slower

    const animateCounters = () => {
        counters.forEach(counter => {
            const updateCount = () => {
                const target = +counter.innerText.replace(/[^\d.]/g, ''); // Get number even if it has % or M
                const count = +counter.getAttribute('data-count') || 0;

                // Keep the suffix (%, M, etc)
                const suffix = counter.innerText.match(/[^\d.]+/) || '';

                const inc = target / speed;

                if (count < target) {
                    const newCount = count + inc;
                    counter.setAttribute('data-count', newCount);
                    counter.innerText = Math.ceil(newCount) + suffix;
                    setTimeout(updateCount, 1);
                } else {
                    counter.innerText = target + suffix;
                }
            };

            // Start when in view (using Intersection Observer or simple scroll check)
            // For now, simple trigger
            updateCount();
        });
    };

    // Trigger counters when impact section is reached
    const impactSection = document.querySelector('.impact');
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            animateCounters();
            observer.unobserve(impactSection);
        }
    }, { threshold: 0.5 });

    if (impactSection) {
        observer.observe(impactSection);
    }

    // Hide loader and animate logo image
    const loader = document.querySelector('.loader-wrapper');
    const animLogo = document.getElementById('animated-logo');

    if (loader) {
        // Step 1: Fade in the logo image immediately
        if (animLogo) {
            setTimeout(() => {
                animLogo.style.opacity = '1';
                animLogo.style.transform = 'scale(1)';
            }, 500);
        }

        // Step 2: Hide loader after animation completion
        setTimeout(() => {
            loader.classList.add('fade-out');
            document.body.style.overflow = 'auto';
        }, 5000);
    }
});
