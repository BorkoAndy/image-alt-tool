# Contao Integration Protocol: Image Alt Generator

This document contains the definitive configuration and logic required to integrate the `image-alt-tool` API into the Contao CMS backend. 

## 1. API Specifications
- **Base URL**: `https://image-alt-tool.vercel.app/api/analyze`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "image_data": "base64_string (including data:image/...;base64, prefix)",
    "model": "gemini",
    "lang": "English/German/etc"
  }
  ```
- **Constraint**: Must be called from the browser (backend) to allow processing of local/protected images.

## 2. Contao DCA Injection
**Path**: `contao/dca/tl_files.php`
```php
<?php
// Inject the generator script into the backend
if (TL_MODE == 'BE') {
    $GLOBALS['TL_JAVASCRIPT'][] = 'bundles/app/js/contao-alt-generator.js';
}
```

## 3. Backend Logic (JavaScript)
**Path**: `public/bundles/app/js/contao-alt-generator.js`
```javascript
(function() {
    'use strict';
    const API_URL = 'https://image-alt-tool.vercel.app/api/analyze';

    function init() {
        if (!document.body.classList.contains('tl_files')) return;
        const observer = new MutationObserver(() => injectButtons());
        observer.observe(document.body, { childList: true, subtree: true });
        injectButtons();
    }

    function injectButtons() {
        const altInputs = document.querySelectorAll('input[name*="[alt]"]');
        altInputs.forEach(input => {
            if (input.dataset.altGenProcessed) return;
            input.dataset.altGenProcessed = "true";
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'tl_submit';
            btn.style.marginLeft = '5px';
            btn.style.padding = '2px 8px';
            btn.innerHTML = '✨ Generate Alt';
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                await handleGeneration(input, btn);
            });
            input.parentNode.insertBefore(btn, input.nextSibling);
            input.style.width = 'calc(100% - 110px)';
            input.style.display = 'inline-block';
        });
    }

    async function handleGeneration(targetInput, btn) {
        const originalText = btn.innerHTML;
        try {
            const previewImg = document.querySelector('.cto_image_preview img, .preview_image img, .image_container img');
            if (!previewImg) throw new Error('Preview not found');
            btn.innerHTML = '⏳ Analyzing...';
            btn.disabled = true;
            const response = await fetch(previewImg.src);
            const blob = await response.blob();
            const base64Data = await new Promise(r => {
                const reader = new FileReader();
                reader.onloadend = () => r(reader.result);
                reader.readAsDataURL(blob);
            });
            const lang = targetInput.name.match(/\[(\w{2})\]/)?.[1] === 'de' ? 'German' : 'English';
            const apiRes = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_data: base64Data, model: 'gemini', lang: lang })
            });
            const data = await apiRes.json();
            if (data.alt_text) {
                targetInput.value = data.alt_text;
                btn.innerHTML = '✅ Done';
            } else throw new Error(data.error);
        } catch (err) {
            alert('Error: ' + err.message);
            btn.innerHTML = '❌ Fail';
        } finally {
            setTimeout(() => { btn.innerHTML = originalText; btn.disabled = false; }, 2000);
        }
    }
    init();
})();
```

## 4. Implementation Steps
1. Ensure the Python API on Vercel is updated to handle `image_data` (base64).
2. Create the DCA file in the Contao project.
3. Create the JS file in the Contao project.
4. Update the Symfony cache in Contao: `bin/console cache:clear`.
