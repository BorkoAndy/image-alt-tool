/**
 * Image ALT Text Generator - Main Script
 */

const SELECTORS = {
    urlInput: '#url-input',
    modelSelect: '#model-select',
    langSelect: '#lang-select',
    btn: '#btn',
    result: '#result',
    altText: '#alt-text',
    charCount: '#char-count',
    error: '#error',
    preview: '#preview',
    previewImg: '#preview-img',
    limits: '#limits',
    rpmRemaining: '#rpm-remaining',
    rpmLimit: '#rpm-limit',
    rpdRemaining: '#rpd-remaining',
    rpdLimit: '#rpd-limit',
    themeToggle: '#theme-toggle',
    themeIcon: '#theme-toggle-icon'
};

/**
 * Theme Management
 */
function initTheme() {
    const theme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        document.querySelector(SELECTORS.themeIcon).textContent = '☀️';
    } else {
        document.documentElement.classList.remove('dark');
        document.querySelector(SELECTORS.themeIcon).textContent = '🌙';
    }
}

function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    document.querySelector(SELECTORS.themeIcon).textContent = isDark ? '☀️' : '🌙';
}

/**
 * Image Analysis Logic
 */
async function analyze() {
    const url = document.querySelector(SELECTORS.urlInput).value.trim();
    const btn = document.querySelector(SELECTORS.btn);
    const result = document.querySelector(SELECTORS.result);
    const altText = document.querySelector(SELECTORS.altText);
    const error = document.querySelector(SELECTORS.error);
    const model = document.querySelector(SELECTORS.modelSelect).value;
    const lang = document.querySelector(SELECTORS.langSelect).value;

    if (!url) return;

    // UI Feedback
    btn.disabled = true;
    const originalBtnText = btn.textContent;
    btn.classList.add('opacity-50', 'cursor-not-allowed');
    btn.textContent = "Analyzing...";
    result.classList.add('hidden');
    error.classList.add('hidden');

    try {
        const res = await fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, model, lang })
        });

        const data = await res.json();

        if (data.alt_text) {
            // Success
            altText.textContent = data.alt_text;
            document.querySelector(SELECTORS.charCount).textContent = `${data.alt_text.length} characters`;
            result.classList.remove('hidden');

            // Update Limits
            if (data.limits) {
                document.querySelector(SELECTORS.rpmRemaining).textContent = data.limits.rpm_remaining;
                document.querySelector(SELECTORS.rpmLimit).textContent = data.limits.rpm_limit;
                document.querySelector(SELECTORS.rpdRemaining).textContent = data.limits.rpd_remaining;
                document.querySelector(SELECTORS.rpdLimit).textContent = data.limits.rpd_limit;
                document.querySelector(SELECTORS.limits).classList.remove('hidden');
                document.querySelector(SELECTORS.limits).classList.add('flex');
            } else {
                document.querySelector(SELECTORS.limits).classList.add('hidden');
            }
        } else {
            throw new Error(data.error || "No result returned");
        }
    } catch (e) {
        error.textContent = "Error: " + (e.message || "unknown error");
        error.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed');
        btn.textContent = originalBtnText;
    }
}

// Preview logic
document.querySelector(SELECTORS.urlInput).addEventListener("input", function () {
    const url = this.value.trim();
    const preview = document.querySelector(SELECTORS.preview);
    const img = document.querySelector(SELECTORS.previewImg);
    
    if (url) {
        img.src = url;
        img.onload = () => preview.classList.remove('hidden');
        img.onerror = () => preview.classList.add('hidden');
    } else {
        preview.classList.add('hidden');
    }
});

// Event Listeners
document.querySelector(SELECTORS.btn).addEventListener('click', analyze);
document.querySelector(SELECTORS.themeToggle).addEventListener('click', toggleTheme);

// Initialize
initTheme();
