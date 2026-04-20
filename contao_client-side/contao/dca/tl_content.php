<?php

/**
 * Contao Open Source CMS
 *
 * Copyright (c) 2005-2024 Leo Feyer
 *
 * @package   ohb
 * @author    Antigravity AI
 * @license   LGPL
 * @copyright Antigravity AI 2024
 */

use Contao\System;
use Symfony\Component\HttpFoundation\Request;

/**
 * Inject the AI Alt-Text generator script into the backend for content elements
 */
try {
    $container = System::getContainer();
    $request = $container->get('request_stack')->getCurrentRequest() ?? Request::createFromGlobals();
    $scopeMatcher = $container->get('contao.routing.scope_matcher');

    if ($scopeMatcher->isBackendRequest($request)) {
        $GLOBALS['TL_JAVASCRIPT'][] = 'js/contao-alt-generator.js';
    }
} catch (\Exception $e) {
    $GLOBALS['TL_JAVASCRIPT'][] = 'js/contao-alt-generator.js';
}
