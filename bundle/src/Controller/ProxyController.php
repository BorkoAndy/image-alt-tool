<?php

namespace NcWerbung\ContaoAiAltTextBundle\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Contracts\HttpClient\HttpClientInterface;

class ProxyController extends AbstractController
{
    private HttpClientInterface $httpClient;
    private string $apiUrl;
    private string $apiKey;
    private string $model;

    public function __construct(
        HttpClientInterface $httpClient,
        string $apiUrl,
        string $apiKey,
        string $model
    ) {
        $this->httpClient = $httpClient;
        $this->apiUrl = $apiUrl;
        $this->apiKey = $apiKey;
        $this->model = $model;
    }

    #[Route('/contao-ai-alt-text/proxy', name: 'nc_werbung_ai_alt_text_proxy', methods: ['POST'])]
    public function __invoke(Request $request): JsonResponse
    {
        $content = $request->getContent();
        $data = json_decode($content, true);

        if (null === $data) {
            return new JsonResponse(['error' => 'Invalid JSON'], 400);
        }

        try {
            $response = $this->httpClient->request('POST', $this->apiUrl, [
                'headers' => [
                    'Content-Type' => 'application/json',
                    'X-API-Key' => $this->apiKey,
                ],
                'json' => $data,
                'timeout' => 30,
            ]);

            return new JsonResponse($response->toArray(false), $response->getStatusCode());
        } catch (\Exception $e) {
            return new JsonResponse(['error' => 'Proxy error: ' . $e->getMessage()], 500);
        }
    }
}
