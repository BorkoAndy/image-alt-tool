# NC-Werbung AI Alt-Text Generator Bundle

This Contao 5 bundle integrates an AI-powered alternative text generator into the Contao backend. 
It supports automatically generating Alt-Text, Titles, and Captions for images in:
- File Manager (`tl_files`)
- Content Elements (`tl_content`)
- News Entries (`tl_news`)

## Installation

1. Search for `nc-werbung/contao-ai-alt-text-bundle` in the Contao Manager and install it.
2. Or use composer:
   ```bash
   composer require nc-werbung/contao-ai-alt-text-bundle
   ```

## Configuration

Add your API credentials to your project's `config/config.yaml`:

```yaml
nc_werbung_ai_alt_text:
    api_url: 'https://image-alt-tool.vercel.app/api/v1/analyze'
    api_key: 'YOUR_SECRET_APP_PASSWORD'
    model: 'groq' # or 'gemini'
```

## How it works

The bundle injects a "✨ Generate" button next to metadata fields in the backend. 
When clicked, it sends the image preview via a secure server-side proxy to the NC-Werbung AI API. 
The AI analyzes the image and returns the metadata in the appropriate languages.

---
© 2024 NC Werbung
