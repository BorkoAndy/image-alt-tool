<?php

namespace NcWerbung\ContaoAiAltTextBundle\DependencyInjection;

use Symfony\Component\Config\Definition\Builder\TreeBuilder;
use Symfony\Component\Config\Definition\ConfigurationInterface;

class Configuration implements ConfigurationInterface
{
    /**
     * {@inheritdoc}
     */
    public function getConfigTreeBuilder(): TreeBuilder
    {
        $treeBuilder = new TreeBuilder('nc_werbung_ai_alt_text');
        $rootNode = $treeBuilder->getRootNode();

        $rootNode
            ->children()
                ->scalarNode('api_url')
                    ->defaultValue('https://image-alt-tool.vercel.app/api/v1/analyze')
                ->end()
                ->scalarNode('api_key')
                    ->defaultValue('')
                ->end()
                ->scalarNode('model')
                    ->defaultValue('groq')
                ->end()
            ->end()
        ;

        return $treeBuilder;
    }
}
