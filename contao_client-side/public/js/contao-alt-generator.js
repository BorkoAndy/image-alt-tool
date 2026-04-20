(function () {
    'use strict';

    console.log('Contao Alt Generator Loaded (V2.0)');

    const API_URL = '/api/analyze.php';
    const APP_PASSWORD = 'Kx9#mP2vN$qL8@wR5yT!'; // Update this to match your APP_PASSWORD


    function init() {
        const observer = new MutationObserver(() => injectButtons());
        observer.observe(document.body, { childList: true, subtree: true });
        injectButtons();
    }

    function injectButtons() {
        // --- tl_files: inject button next to "Metadaten" heading ---
        const metaLists = document.querySelectorAll('ul.tl_metawizard');
        metaLists.forEach(ul => {
            if (ul.dataset.altGenProcessed) return;

            // Check it has at least one language tab
            const langItems = ul.querySelectorAll('li[data-language]');
            if (langItems.length === 0) return;

            ul.dataset.altGenProcessed = 'true';

            // Find the h3 label above this ul
            const widget = ul.closest('.widget');
            if (!widget) return;
            const h3 = widget.querySelector('h3');
            if (!h3) return;

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'tl_submit';
            btn.style.marginLeft = '10px';
            btn.style.padding = '2px 10px';
            btn.style.fontSize = '0.9em';
            btn.style.verticalAlign = 'middle';
            btn.innerHTML = '✨ Generate All';
            btn.title = 'Generate title, alt text and caption for all languages';

            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                await handleMetaGeneration(btn);
            });

            h3.appendChild(btn);
        });

        // --- tl_content / tl_news: inject per alt field ---
        const altInputs = document.querySelectorAll('input[name="alt"]');
        altInputs.forEach(input => {
            if (input.dataset.altGenProcessed) return;
            input.dataset.altGenProcessed = 'true';

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'tl_submit';
            btn.style.marginLeft = '5px';
            btn.style.padding = '2px 8px';
            btn.innerHTML = '✨ Generate Alt';

            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                await handleSingleGeneration(input, btn);
            });

            input.parentNode.insertBefore(btn, input.nextSibling);
            input.style.width = 'calc(100% - 130px)';
            input.style.display = 'inline-block';
        });
    }

    function getPreviewImage() {
        // Find the image preview on the page
        const selectors = [
            '.cto_image_preview img',
            '.preview_image img',
            '.image_container img',
            '[class*="preview"] img',
            '.tl_file_list img'
        ];

        let previewImg = null;
        for (const selector of selectors) {
            previewImg = document.querySelector(selector);
            if (previewImg && previewImg.src && !previewImg.src.includes('spacer.gif')) break;
        }

        // Fallback: look near singleSRC field
        if (!previewImg || previewImg.src.includes('spacer.gif')) {
            const containers = document.querySelectorAll('.w50, .w100, .widget');
            for (const container of containers) {
                if (
                    container.innerText.includes('Quell') ||
                    container.innerText.includes('Source') ||
                    container.querySelector('[name="singleSRC"]')
                ) {
                    const img = container.querySelector('img');
                    if (img && img.src && !img.src.includes('spacer.gif')) {
                        previewImg = img;
                        break;
                    }
                }
            }
        }

        return previewImg;
    }

    function detectLanguages() {
        // Read language codes from li[data-language] — works for any language
        const langItems = document.querySelectorAll('ul.tl_metawizard li[data-language]');
        const languages = [];
        langItems.forEach(li => {
            const lang = li.getAttribute('data-language');
            if (lang && !languages.includes(lang)) {
                languages.push(lang);
            }
        });
        return languages; // e.g. ["de", "en", "ru"]
    }

    async function fetchImageAsBase64(src) {
        const response = await fetch(src);
        if (!response.ok) throw new Error('Failed to fetch image preview.');
        const blob = await response.blob();
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.readAsDataURL(blob);
        });
    }

    async function handleMetaGeneration(btn) {
        const originalText = btn.innerHTML;
        try {
            const previewImg = getPreviewImage();
            if (!previewImg) throw new Error('Image preview not found. Please ensure the image is visible.');

            const languages = detectLanguages();
            if (languages.length === 0) throw new Error('No language tabs found.');

            console.log('Detected languages:', languages);

            btn.innerHTML = '⏳ Analyzing...';
            btn.disabled = true;

            const base64Data = await fetchImageAsBase64(previewImg.src);

            const apiRes = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image_data: base64Data,
                    model: 'groq',
                    languages: languages,
                    password: APP_PASSWORD
                })
            });

            if (!apiRes.ok) {
                const errorData = await apiRes.json();
                throw new Error(errorData.error || 'API Error ' + apiRes.status);
            }

            const data = await apiRes.json();

            // Fill all fields for all detected languages
            // data.meta = { de: { alt, title, caption }, en: { alt, title, caption }, ru: {...}, ... }
            if (data.meta) {
                languages.forEach(lang => {
                    const langData = data.meta[lang];
                    if (!langData) return;

                    const altInput = document.querySelector(`input[name="meta[${lang}][alt]"]`);
                    const titleInput = document.querySelector(`input[name="meta[${lang}][title]"]`);
                    const captionInput = document.querySelector(`textarea[name="meta[${lang}][caption]"]`);

                    if (altInput && langData.alt) altInput.value = langData.alt;
                    if (titleInput && langData.title) titleInput.value = langData.title;
                    if (captionInput && langData.caption) captionInput.value = langData.caption;
                });

                btn.innerHTML = '✅ Done';
            } else {
                throw new Error(data.error || 'Empty response from AI');
            }

        } catch (err) {
            console.error('Alt Gen Error:', err);
            alert('Error: ' + err.message);
            btn.innerHTML = '❌ Failed';
        } finally {
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 2000);
        }
    }

    async function handleSingleGeneration(targetInput, btn) {
        const originalText = btn.innerHTML;
        try {
            const previewImg = getPreviewImage();
            if (!previewImg) throw new Error('Image preview not found. Please ensure the image is selected and visible.');

            btn.innerHTML = '⏳ Analyzing...';
            btn.disabled = true;

            const base64Data = await fetchImageAsBase64(previewImg.src);

            // Detect language from input name or page language
            const langMatches = targetInput.name.match(/\[(\w{2,3})\]/);
            const langCode = langMatches ? langMatches[1] : (document.documentElement.lang || 'en');
            const lang = langCode.startsWith('de') ? 'German' : 'English';

            const apiRes = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image_data: base64Data,
                    model: 'groq',
                    lang: lang,
                    password: APP_PASSWORD
                })
            });

            if (!apiRes.ok) {
                const errorData = await apiRes.json();
                throw new Error(errorData.error || 'API Error ' + apiRes.status);
            }

            const data = await apiRes.json();

            if (data.alt_text) {
                targetInput.value = data.alt_text;
                btn.innerHTML = '✅ Done';
            } else {
                throw new Error(data.error || 'Empty response from AI');
            }

        } catch (err) {
            console.error('Alt Gen Error:', err);
            alert('Error: ' + err.message);
            btn.innerHTML = '❌ Failed';
        } finally {
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 2000);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
