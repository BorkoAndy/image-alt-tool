# Contao Integration Protocol: Image Alt Generator (v1 REST API)

This document contains the definitive configuration and logic required to integrate the `image-alt-tool` API into the Contao CMS backend.

## 1. API Specifications (v1)
- **Base URL**: `https://image-alt-tool.vercel.app/api/v1/analyze`
- **Method**: `POST`
- **Headers**:
  - `X-API-Key`: `YOUR_APP_PASSWORD`
  - `Content-Type`: `application/json`
- **Payload**:
  ```json
  {
    "image_data": "base64_string",
    "model": "groq",
    "languages": ["de", "en"],
    "lang": "English"
  }
  ```

## 2. Security: The PHP Proxy
To avoid CORS issues and protect your API key from being exposed in the browser, all requests should go through a server-side proxy on your Contao installation.

**Path**: `public/api/analyze.php`
```php
<?php
header('Content-Type: application/json');
$api_url = 'https://image-alt-tool.vercel.app/api/v1/analyze';
$api_key = 'YOUR_APP_PASSWORD'; // Set securely here

$input_data = file_get_contents('php://input');

$ch = curl_init($api_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $input_data);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-API-Key: ' . $api_key
]);

$response = curl_exec($ch);
$http_status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

http_response_code($http_status);
echo $response;
```

## 3. Contao DCA Injection
**Path**: `contao/dca/tl_files.php`
```php
<?php
if (TL_MODE == 'BE') {
    $GLOBALS['TL_JAVASCRIPT'][] = 'js/contao-alt-generator.js';
}
```

## 4. Backend Logic (JavaScript)
**Path**: `public/js/contao-alt-generator.js`
Update the `API_URL` to point to your **local proxy** or directly to the API if preferred.

```javascript
const API_URL = '/api/analyze.php'; // Point to your local PHP proxy
// ... rest of the logic as defined in the repo ...
```

## 5. Implementation Steps
1. Verify the Python API on Vercel is set up with `APP_PASSWORD`.
2. Deploy the PHP proxy to your Contao server's `public/api/` folder.
3. Add the DCA configuration.
4. Upload the JavaScript integration script.
5. Clear Contao cache: `php bin/console cache:clear`.
