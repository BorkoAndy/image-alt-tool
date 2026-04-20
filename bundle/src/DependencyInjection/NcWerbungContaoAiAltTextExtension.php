<?php

namespace NcWerbung\ContaoAiAltTextBundle\DependencyInjection;

use Symfony\Component\Config\FileLocator;
use Symfony\Component\DependencyInjection\ContainerBuilder;
use Symfony\Component\DependencyInjection\Extension\Extension;
use Symfony\Component\DependencyInjection\Loader\YamlFileLoader;

class NcWerbungContaoAiAltTextExtension extends Extension
{
    /**
     * {@inheritdoc}
     */
    public function load(array $configs, ContainerBuilder $container): void
    {
        $configuration = new Configuration();
        $config = $this->processConfiguration($configuration, $configs);

        $container->setParameter('nc_werbung_ai_alt_text.api_url', $config['api_url']);
        $container->setParameter('nc_werbung_ai_alt_text.api_key', $config['api_key']);
        $container->setParameter('nc_werbung_ai_alt_text.model', $config['model']);

        $loader = new YamlFileLoader($container, new FileLocator(__DIR__ . '/../../config'));
        $loader->load('services.yaml');
    }
}
