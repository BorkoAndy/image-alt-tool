<?php

namespace NcWerbung\ContaoAiAltTextBundle\ContaoManager;

use Contao\CoreBundle\ContaoCoreBundle;
use Contao\ManagerPlugin\Bundle\BundlePluginInterface;
use Contao\ManagerPlugin\Bundle\Config\BundleConfig;
use Contao\ManagerPlugin\Bundle\Parser\ParserInterface;
use NcWerbung\ContaoAiAltTextBundle\NcWerbungContaoAiAltTextBundle;

class Plugin implements BundlePluginInterface
{
    /**
     * {@inheritdoc}
     */
    public function getBundles(ParserInterface $parser): array
    {
        return [
            BundleConfig::create(NcWerbungContaoAiAltTextBundle::class)
                ->setLoadAfter([ContaoCoreBundle::class]),
        ];
    }
}
