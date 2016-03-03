<?php

require_once '/usr/share/php/fkooman/Config/autoload.php';

use fkooman\Config\YamlFile;

$configFiles = [
    '/etc/vpn-ca-api/config.yaml' => 's',
    '/etc/vpn-server-api/config.yaml' => 's',
    '/etc/vpn-user-portal/config.yaml' => 'c',
    '/etc/vpn-admin-portal/config.yaml' => 'c',
];

try {
    if (2 > $argc) {
        throw new Exception(
            sprintf('SYNTAX: %s [apiSecret]', $argv[0])
        );
    }
    $apiSecret = $argv[1];
    foreach ($configFiles as $configFile => $type) {
        $yamlFile = new YamlFile($configFile);
        $configData = $yamlFile->readConfig();
        if ('c' === $type) {
            $configData['ConfigApi']['Secret'] = $apiSecret;
            $configData['ServerApi']['Secret'] = $apiSecret;
        } elseif ('s' === $type) {
            $configData['Api'] = [$apiSecret];
        } else {
            // NOP
        }
        $yamlFile->writeConfig($configData);
    }
} catch (Exception $e) {
    echo $e->getMessage().PHP_EOL;
    exit(1);
}
