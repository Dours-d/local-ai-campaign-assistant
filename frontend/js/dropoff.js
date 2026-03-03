/**
 * FAJR DROPOFF SYSTEM
 * Manages the dynamic product feed and sovereign settlement modal.
 */

const PRODUCT_DATA_URL = 'data/products.json';

/**
 * Initialize the product feed.
 */
async function initProductFeed() {
    const container = document.getElementById('product-grid');
    if (!container) return;

    try {
        const response = await fetch(PRODUCT_DATA_URL);
        if (!response.ok) throw new Error('Could not load product data.');

        const products = await response.json();
        renderProducts(products);
    } catch (error) {
        console.error('Error loading products:', error);
        // Fallback to static content if fetch fails
    }
}

/**
 * Render products into the grid.
 * @param {Array} products 
 */
function renderProducts(products) {
    const container = document.getElementById('product-grid');
    container.innerHTML = ''; // Clear for fresh render

    products.forEach((product, index) => {
        const delay = (index % 3) * 100;
        const card = document.createElement('div');
        card.className = 'card-trust';
        card.setAttribute('data-aos', 'fade-up');
        card.setAttribute('data-aos-delay', delay);

        card.innerHTML = `
            <div class="card-visual product-placeholder" style="background-image: url('${product.media?.main_image || ''}')">
                ${!product.media?.main_image ? 'AMANAH VERIFIED' : ''}
            </div>
            <div>
                <div class="trust-badge"><span class="trust-dot"></span>SOVEREIGN ORIGIN VERIFIED</div>
                <h3 class="lang-dual">
                    <span class="ar-main">${product.title_ar || ''}</span>
                    <span class="en-sub">${product.product_info.title}</span>
                </h3>
                <p style="margin-top: 15px; color: var(--color-text-dim);">${product.product_info.short_description}</p>
                <div class="tags" style="margin-top: 20px;">
                    ${product.product_info.tags.slice(0, 3).map(tag => `<span class="tag">${tag.toUpperCase()}</span>`).join('')}
                </div>
            </div>
            <div>
                <div class="product-price">$${product.pricing.retail_price_usd.toFixed(2)} <small>USDT / EUR</small></div>
                <button onclick="showSovereignModal('${product.product_info.title.replace(/'/g, "\\'")}', '$${product.pricing.retail_price_usd.toFixed(2)}')" class="btn btn-primary w-full">RESERVE & SETTLE</button>
            </div>
        `;
        container.appendChild(card);
    });

    // Re-initialize AOS for new elements
    if (window.AOS) {
        window.AOS.refresh();
    }
}

// Stats counter animation
function animateStats() {
    const stats = [
        { id: 'stat-settlements', end: 152 },
        { id: 'stat-volume', end: 8420, prefix: '$' },
        { id: 'stat-friction', end: 0, suffix: '%' },
        { id: 'stat-trust', end: 100, suffix: '%' }
    ];

    stats.forEach(stat => {
        const el = document.getElementById(stat.id);
        if (!el) return;

        let current = 0;
        const duration = 2000;
        const stepTime = 20;
        const increment = stat.end / (duration / stepTime);

        const timer = setInterval(() => {
            current += increment;
            if (current >= stat.end) {
                current = stat.end;
                clearInterval(timer);
            }
            let val = Math.floor(current);
            if (stat.prefix) val = stat.prefix + val.toLocaleString();
            if (stat.suffix) val = val + stat.suffix;
            el.innerText = val;
        }, stepTime);
    });
}

// Run on load
document.addEventListener('DOMContentLoaded', () => {
    // animateStats(); // Should be triggered by intersection observer for better UX
});

// Intersection Observer for stats
const observerOptions = {
    threshold: 0.5
};

const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateStats();
            statsObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

const impactSection = document.querySelector('.impact-ledger');
if (impactSection) {
    statsObserver.observe(impactSection);
}
