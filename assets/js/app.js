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
    themeIcon: '#theme-toggle-icon',
    sliderTrack: '#slider-track',
    sliderHandle: '#slider-handle',
    sliderText: '#slider-text',
    loginOverlay: '#login-overlay',
    loginForm: '#login-form',
    loginPassword: '#login-password'
};

let isVerified = false;

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
 * Authentication Management
 */
function getAuth() {
    return localStorage.getItem('app_password');
}

function setAuth(password) {
    localStorage.setItem('app_password', password);
}

function clearAuth() {
    localStorage.removeItem('app_password');
}

function checkAuth() {
    const overlay = document.querySelector(SELECTORS.loginOverlay);
    const password = getAuth();
    
    if (!password) {
        overlay.classList.remove('opacity-0', 'pointer-events-none');
        overlay.querySelector('div').classList.remove('scale-95');
        overlay.querySelector('div').classList.add('scale-100');
        return false;
    } else {
        overlay.classList.add('opacity-0', 'pointer-events-none');
        overlay.querySelector('div').classList.add('scale-95');
        overlay.querySelector('div').classList.remove('scale-100');
        return true;
    }
}

function initAuth() {
    const form = document.querySelector(SELECTORS.loginForm);
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const password = document.querySelector(SELECTORS.loginPassword).value;
        if (password) {
            setAuth(password);
            checkAuth();
        }
    });

    checkAuth();
}

/**
 * Slider Verification Logic
 */
function initSlider() {
    const track = document.querySelector(SELECTORS.sliderTrack);
    const handle = document.querySelector(SELECTORS.sliderHandle);
    const text = document.querySelector(SELECTORS.sliderText);
    const btn = document.querySelector(SELECTORS.btn);
    const urlInput = document.querySelector(SELECTORS.urlInput);

    let isDragging = false;
    let startX = 0;
    let currentX = 0;

    const startDrag = (e) => {
        if (isVerified || !urlInput.value.trim()) return;
        isDragging = true;
        startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
        handle.classList.remove('transition-transform');
        handle.classList.add('scale-105');
    };

    const moveDrag = (e) => {
        if (!isDragging) return;
        
        const clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
        const maxDelta = track.clientWidth - handle.clientWidth - 8;
        currentX = Math.max(0, Math.min(clientX - startX, maxDelta));
        
        handle.style.transform = `translateX(${currentX}px)`;
        text.style.opacity = 1 - (currentX / maxDelta);
        
        if (currentX >= maxDelta) {
            completeVerification();
        }
    };

    const endDrag = () => {
        if (!isDragging) return;
        isDragging = false;
        if (!isVerified) {
            resetSlider();
        }
    };

    const resetSlider = () => {
        handle.style.transform = `translateX(0px)`;
        handle.classList.add('transition-transform');
        handle.classList.remove('scale-105');
        text.style.opacity = 1;
    };

    const completeVerification = () => {
        isVerified = true;
        isDragging = false;
        handle.style.transform = `translateX(${track.clientWidth - handle.clientWidth - 8}px)`;
        handle.classList.add('bg-green-500');
        handle.classList.remove('bg-indigo-600', 'hover:bg-indigo-700', 'cursor-grab');
        handle.querySelector('span').textContent = '✓';
        text.textContent = 'Verified';
        text.classList.remove('text-gray-400');
        text.classList.add('text-green-500', 'font-bold');
        
        track.classList.add('border-green-500', 'bg-green-50/50', 'dark:bg-green-900/10');
        
        // Unlock analyze button
        btn.classList.remove('hidden');
        btn.disabled = false;
        
        // Auto-trigger analysis for smoother UX
        analyze();
    };

    // Event Listeners
    handle.addEventListener('mousedown', startDrag);
    window.addEventListener('mousemove', moveDrag);
    window.addEventListener('mouseup', endDrag);

    handle.addEventListener('touchstart', startDrag);
    window.addEventListener('touchmove', moveDrag);
    window.addEventListener('touchend', endDrag);
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

    if (!url || !isVerified) return;

    // UI Feedback
    btn.disabled = true;
    const originalBtnText = btn.textContent;
    btn.classList.add('opacity-50', 'cursor-not-allowed');
    btn.textContent = "Analyzing...";
    result.classList.add('hidden');
    error.classList.add('hidden');

    try {
        const password = getAuth();
        const res = await fetch("/api/analyze", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": password
            },
            body: JSON.stringify({ url, model, lang })
        });

        if (res.status === 401) {
            clearAuth();
            checkAuth();
            throw new Error("Invalid password. Please try again.");
        }

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
        // Reset verification on error if it's a content/validation error
        resetVerificationState();
    } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed');
        btn.textContent = originalBtnText;
    }
}

function resetVerificationState() {
    isVerified = false;
    const handle = document.querySelector(SELECTORS.sliderHandle);
    const track = document.querySelector(SELECTORS.sliderTrack);
    const text = document.querySelector(SELECTORS.sliderText);
    const btn = document.querySelector(SELECTORS.btn);

    handle.style.transform = `translateX(0px)`;
    handle.classList.remove('bg-green-500');
    handle.classList.add('bg-indigo-600', 'hover:bg-indigo-700', 'cursor-grab');
    handle.querySelector('span').textContent = '→';
    
    text.textContent = 'Slide to Analyze';
    text.classList.remove('text-green-500', 'font-bold');
    text.classList.add('text-gray-400');
    text.style.opacity = 1;

    track.classList.remove('border-green-500', 'bg-green-50/50', 'dark:bg-green-900/10');
    btn.classList.add('hidden');
}

// Preview logic
document.querySelector(SELECTORS.urlInput).addEventListener("input", function () {
    const url = this.value.trim();
    const preview = document.querySelector(SELECTORS.preview);
    const img = document.querySelector(SELECTORS.previewImg);
    
    // reset verification if url changes
    if (isVerified) resetVerificationState();

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
initSlider();
initAuth();
