// App Galaxy - JavaScript
// Handles app filtering, search, and installation

document.addEventListener('DOMContentLoaded', () => {
    initCategoryFilters();
    initSearch();
    initInstallButtons();
});

// ===== Category Filtering =====
function initCategoryFilters() {
    const tabs = document.querySelectorAll('.cat-tab');
    const apps = document.querySelectorAll('.app-card');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const category = tab.dataset.category;

            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Filter apps
            apps.forEach(app => {
                if (category === 'all' || app.dataset.category === category) {
                    app.style.display = 'flex';
                } else {
                    app.style.display = 'none';
                }
            });
        });
    });
}

// ===== Search =====
function initSearch() {
    const searchInput = document.getElementById('searchInput');

    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase();
        const apps = document.querySelectorAll('.app-card');

        apps.forEach(app => {
            const title = app.querySelector('h3').textContent.toLowerCase();
            const desc = app.querySelector('.app-desc').textContent.toLowerCase();

            if (title.includes(query) || desc.includes(query)) {
                app.style.display = 'flex';
            } else {
                app.style.display = 'none';
            }
        });
    });
}

// ===== Install Buttons =====
function initInstallButtons() {
    const buttons = document.querySelectorAll('.app-btn:not(.disabled)');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const appCard = btn.closest('.app-card');
            const appName = appCard.querySelector('h3').textContent;
            const price = appCard.querySelector('.app-price').textContent;

            if (price === 'Free') {
                // Simulate installation
                btn.textContent = 'Installing...';
                btn.disabled = true;
                btn.style.opacity = '0.5';

                setTimeout(() => {
                    btn.textContent = 'Installed ✓';
                    btn.style.background = 'var(--success)';
                    alert(`✅ ${appName} installed successfully!\n\nOpen it from the Apps menu.`);
                }, 2000);
            } else {
                // Simulate subscription
                const confirm = window.confirm(`Subscribe to ${appName} for ${price}?\n\nYou will be charged monthly.`);
                if (confirm) {
                    btn.textContent = 'Subscribed ✓';
                    btn.disabled = true;
                    btn.style.background = 'var(--success)';
                    alert(`✅ Subscribed to ${appName}!\n\nEnjoy premium features.`);
                }
            }
        });
    });

    // Disabled buttons
    const disabledBtns = document.querySelectorAll('.app-btn.disabled');
    disabledBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            alert('🚧 This app is coming soon!\n\nWe are working hard to bring you this feature.\n\nFollow us for updates.');
        });
    });
}

// ===== Publish Button =====
document.querySelector('.publish-section .btn-primary')?.addEventListener('click', () => {
    alert('🎨 Publisher Portal Coming Soon!\n\nPublish your:\n• AI Agents\n• Smart Contract Templates\n• Developer Tools\n• UI Kits\n• Automation Workflows\n\nEarn money from your creations!');
});
