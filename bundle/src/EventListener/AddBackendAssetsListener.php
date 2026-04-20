<?php

namespace NcWerbung\ContaoAiAltTextBundle\EventListener;

use Contao\CoreBundle\Routing\ScopeMatcher;
use Symfony\Component\HttpKernel\Event\RequestEvent;

class AddBackendAssetsListener
{
    private ScopeMatcher $scopeMatcher;

    public function __construct(ScopeMatcher $scopeMatcher)
    {
        $this->scopeMatcher = $scopeMatcher;
    }

    public function __invoke(RequestEvent $event): void
    {
        $request = $event->getRequest();

        if (!$this->scopeMatcher->isBackendRequest($request)) {
            return;
        }

        // Inject the JavaScript file from the bundle's public directory
        // Symlinked by Contao to: public/bundles/ncwerbungcontaoaialttext/js/contao-alt-generator.js
        $GLOBALS['TL_JAVASCRIPT'][] = 'bundles/ncwerbungcontaoaialttext/js/contao-alt-generator.js';
    }
}
