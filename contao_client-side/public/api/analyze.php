<?php

/**
 * AI Alt-Text API Proxy
 * Bypasses CORS restrictions by handling requests server-side.
 * Updated for v1 REST API structure.
 */

header('Content-Type: application/json');

// Target API URL (updated to v1)
$api_url = 'https://image-alt-tool.vercel.app/api/v1/analyze';

// Get raw input
$input_data = file_get_contents('php://input');
$data = json_decode($input_data, true);

// Get headers
$headers = getallheaders();
$api_key = $headers['X-API-Key'] ?? $headers['x-api-key'] ?? '';

// Fallback: if not in headers, check if it's in the JSON body (old style)
if (empty($api_key) && is_array($data) && isset($data['password'])) {
    $api_key = $data['password'];
    // Remove password from data before forwarding if it was there
    unset($data['password']);
    $input_data = json_encode($data);
}

if (empty($input_data)) {
    http_response_code(400);
    echo json_encode(['error' => 'No data provided to proxy']);
    exit;
}

// Initialize cURL session
$ch = curl_init($api_url);

// Set cURL options
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $input_data);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-API-Key: ' . $api_key,
    'User-Agent: Contao-Alt-Generator-Proxy/2.0'
]);

// Timeout settings
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);

// Execute the request
$response = curl_exec($ch);
$error = curl_error($ch);
$http_status = curl_getinfo($ch, CURLINFO_HTTP_CODE);

curl_close($ch);

// Forward the response
if ($error) {
    http_response_code(500);
    echo json_encode(['error' => 'Proxy Error: ' . $error]);
} else {
    http_response_code($http_status);
    echo $response;
}
