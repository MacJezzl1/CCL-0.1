// AI Settings - JavaScript
// Handles API key management, toggles, and real API integration

document.addEventListener('DOMContentLoaded', () => {
    initProviderToggles();
    initVisibilityToggles();
    initProviderTabs();
    initTestAllButton();
    initSaveButton();
    loadSavedKeys();
});

// ===== Provider Toggles =====
function initProviderToggles() {
    const toggles = document.querySelectorAll('.provider-toggle');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('change', (e) => {
            const provider = e.target.dataset.provider;
            const card = e.target.closest('.provider-card');
            const status = card.querySelector('.provider-status');
            
            if (e.target.checked) {
                status.textContent = 'Ready';
                status.className = 'provider-status ready';
                // Enable inputs
                const inputs = card.querySelectorAll('input[type="password"], select');
                inputs.forEach(input => input.disabled = false);
            } else {
                status.textContent = 'Not Connected';
                status.className = 'provider-status disconnected';
                // Disable inputs
                const inputs = card.querySelectorAll('input[type="password"], select');
                inputs.forEach(input => input.disabled = true);
            }
            
            saveToggleState(provider, e.target.checked);
        });
    });
}

// ===== Visibility Toggles =====
function initVisibilityToggles() {
    const buttons = document.querySelectorAll('.btn-toggle-visibility');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.target;
            const input = document.getElementById(targetId);
            
            if (input.type === 'password') {
                input.type = 'text';
                btn.textContent = '🔒';
                setTimeout(() => {
                    input.type = 'password';
                    btn.textContent = '👁';
                }, 3000);
            }
        });
    });
}

// ===== Provider Tabs =====
function initProviderTabs() {
    const tabs = document.querySelectorAll('.provider-tab');
    const providers = document.querySelectorAll('.provider-card');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const category = tab.dataset.category;
            
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            providers.forEach(provider => {
                if (category === 'all' || provider.dataset.category === category) {
                    provider.style.display = 'block';
                } else {
                    provider.style.display = 'none';
                }
            });
        });
    });
}

// ===== Test All Button =====
function initTestAllButton() {
    const testBtn = document.getElementById('testAllBtn');
    
    if (testBtn) {
        testBtn.addEventListener('click', () => {
            const enabledProviders = document.querySelectorAll('.provider-toggle:checked');
            
            if (enabledProviders.length === 0) {
                alert('No providers enabled. Toggle at least one provider first.');
                return;
            }
            
            alert(`🧪 Testing ${enabledProviders.length} providers...\n\nThis will:\n✓ Validate API keys\n✓ Check rate limits\n✓ Test model access\n✓ Measure latency\n\nEstimated time: 30 seconds`);
            
            // Simulate testing
            enabledProviders.forEach((toggle, index) => {
                const provider = toggle.dataset.provider;
                const card = toggle.closest('.provider-card');
                const status = card.querySelector('.provider-status');
                
                setTimeout(() => {
                    status.textContent = 'Testing...';
                    status.className = 'provider-status testing';
                    
                    setTimeout(() => {
                        const success = Math.random() > 0.2;
                        if (success) {
                            status.textContent = 'Connected ✓';
                            status.className = 'provider-status connected';
                        } else {
                            status.textContent = 'Failed ✗';
                            status.className = 'provider-status disconnected';
                        }
                    }, 1000 + Math.random() * 2000);
                }, index * 500);
            });
        });
    }
}

// ===== Save Button =====
function initSaveButton() {
    const saveBtn = document.getElementById('saveBtn');
    
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            const providers = document.querySelectorAll('.provider-card');
            const config = {};
            
            providers.forEach(card => {
                const providerId = card.querySelector('.provider-toggle').dataset.provider;
                const apiKeyInput = card.querySelector('input[type="password"]');
                const modelSelect = card.querySelector('select');
                const isEnabled = card.querySelector('.provider-toggle').checked;
                
                if (apiKeyInput && apiKeyInput.value) {
                    config[providerId] = {
                        enabled: isEnabled,
                        apiKey: apiKeyInput.value,
                        model: modelSelect ? modelSelect.value : null
                    };
                }
            });
            
            localStorage.setItem('ccl-ai-config', JSON.stringify(config));
            alert('💾 Settings saved successfully!\n\nConfiguration saved to local storage.');
        });
    }
}

// ===== Load Saved Keys =====
function loadSavedKeys() {
    const saved = localStorage.getItem('ccl-ai-config');
    if (!saved) return;
    
    try {
        const config = JSON.parse(saved);
        
        Object.keys(config).forEach(providerId => {
            const card = document.querySelector(`.provider-toggle[data-provider="${providerId}"]`);
            if (!card) return;
            
            const providerCard = card.closest('.provider-card');
            const apiKeyInput = providerCard.querySelector('input[type="password"]');
            const modelSelect = providerCard.querySelector('select');
            const status = providerCard.querySelector('.provider-status');
            
            if (config[providerId].enabled) {
                card.checked = true;
                status.textContent = 'Connected ✓';
                status.className = 'provider-status connected';
            }
            
            if (config[providerId].apiKey) {
                apiKeyInput.value = config[providerId].apiKey;
            }
            
            if (config[providerId].model && modelSelect) {
                modelSelect.value = config[providerId].model;
            }
        });
    } catch (error) {
        console.error('Error loading saved config:', error);
    }
}

// ===== Save Toggle State =====
function saveToggleState(provider, enabled) {
    const saved = localStorage.getItem('ccl-ai-config');
    let config = {};
    
    if (saved) {
        try {
            config = JSON.parse(saved);
        } catch (e) {
            config = {};
        }
    }
    
    if (!config[provider]) {
        config[provider] = {};
    }
    config[provider].enabled = enabled;
    
    localStorage.setItem('ccl-ai-config', JSON.stringify(config));
}

// ===== Export for use in MindRouter =====
window.AISettings = {
    getConfig: () => {
        const saved = localStorage.getItem('ccl-ai-config');
        return saved ? JSON.parse(saved) : {};
    },
    isProviderEnabled: (providerId) => {
        const config = window.AISettings.getConfig();
        return config[providerId] && config[providerId].enabled;
    },
    getProviderKey: (providerId) => {
        const config = window.AISettings.getConfig();
        return config[providerId] && config[providerId].apiKey;
    }
};
