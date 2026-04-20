(function () {
    'use strict';

    console.log('Contao Alt Generator Loaded (V1.2)');

    const API_URL = '/api/analyze.php';
    const APP_PASSWORD = 'Kx9#mP2vN$qL8@wR5yT!'; // Update this to match your Vercel APP_PASSWORD


    function init() {
        // Run on every backend page, but filter inside injectButtons
        const observer = new MutationObserver(() => injectButtons());
        observer.observe(document.body, { childList: true, subtree: true });
        injectButtons();
    }

    function injectButtons() {
        // Find alt inputs: 
        // 1. Standard "alt" field (used in tl_content, tl_news, etc.)
        // 2. Metadata array fields like "metadata[en][alt]" (used in tl_files)
        const altInputs = document.querySelectorAll('input[name="alt"], input[name*="[alt]"]');

        altInputs.forEach(input => {
            if (input.dataset.altGenProcessed) return;
            input.dataset.altGenProcessed = "true";

            console.log('Injecting button for:', input.name);

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'tl_submit';
            btn.style.marginLeft = '5px';
            btn.style.padding = '2px 8px';
            btn.innerHTML = '✨ Generate Alt';
            btn.title = 'Use AI to generate alternative text';

            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                await handleGeneration(input, btn);
            });

            // Insert after the input
            input.parentNode.insertBefore(btn, input.nextSibling);

            // Adjust input style to fit button
            input.style.width = 'calc(100% - 130px)';
            input.style.display = 'inline-block';
        });
    }

    async function handleGeneration(targetInput, btn) {
        const originalText = btn.innerHTML;
        try {
            // Find the image preview in the edit mask
            // We search for standard Contao preview classes and also look for 
            // any image that might be in the same fieldset or container.
            let previewImg = null;
            
            // 1. Try specific container classes
            const selectors = [
                '.cto_image_preview img', 
                '.preview_image img', 
                '.image_container img', 
                '[class*="preview"] img',
                '.tl_file_list img' // Sometimes used in file manager
            ];
            
            for (const selector of selectors) {
                previewImg = document.querySelector(selector);
                if (previewImg && previewImg.src && !previewImg.src.includes('spacer.gif')) break;
            }

            // 2. Fallback: looking for any image in the proximity of "singleSRC" field
            if (!previewImg || previewImg.src.includes('spacer.gif')) {
                const containers = document.querySelectorAll('.w50, .w100, .widget');
                for (const container of containers) {
                    if (container.innerText.includes('Quell') || container.innerText.includes('Source') || container.querySelector('[name="singleSRC"]')) {
                        const img = container.querySelector('img');
                        if (img && img.src && !img.src.includes('spacer.gif')) {
                            previewImg = img;
                            break;
                        }
                    }
                }
            }

            if (!previewImg) {
                throw new Error('Image preview not found. Please ensure the image is selected and visible.');
            }

            btn.innerHTML = '⏳ Analyzing...';
            btn.disabled = true;

            console.log('Fetching image from:', previewImg.src);

            // Fetch the image as blob
            let imageFetchResponse;
            try {
                imageFetchResponse = await fetch(previewImg.src);
            } catch (e) {
                console.error('Local image fetch failed:', e);
                throw new Error('Could not read image. Try saving the element first if the image was just selected.');
            }

            if (!imageFetchResponse.ok) throw new Error('Failed to fetch image preview.');

            const blob = await imageFetchResponse.blob();
            const base64Data = await new Promise((resolve) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result);
                reader.readAsDataURL(blob);
            });

            // Detect language (e.g., metadata[de][alt] or backend page language)
            const langMatches = targetInput.name.match(/\[(\w{2})\]/);
            const langCode = langMatches ? langMatches[1] : (document.documentElement.lang || 'en');
            const lang = langCode.startsWith('de') ? 'German' : 'English';

            console.log('Calling AI API for lang:', lang);

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
                throw new Error('Empty response from AI');
            }
        } catch (err) {
            console.error('Alt Gen Error:', err);
            alert('Error: ' + err.message);
            btn.innerHTML = '❌ Fail';
        } finally {
            setTimeout(() => {
                btn.innerHTML = '🔄 Re-generate';
                btn.disabled = false;
            }, 1000);
        }
    }

    // Run init
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
