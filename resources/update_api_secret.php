<?php

require_once '/usr/share/php/password_compat/password.php';
require_once '/usr/share/php/fkooman/Config/autoload.php';

use fkooman\Config\YamlFile;

#$hashedSecrets = array(
#    '/var/www/vpn-config-api/config/config.yaml' => 'BasicAuthentication',
#    '/var/www/vpn-server-api/config/config.yaml' => 'Users',
#    '/var/www/vpn-user-portal/config/config.yaml' => 'ApiAuthentication',
#);

#$plainSecrets = array(
#    '/var/www/vpn-user-portal/config/config.yaml' => array('VpnConfigApi', 'VpnServerApi'),
#    '/var/www/vpn-admin-portal/config/config.yaml' => array('VpnServerApi', 'VpnUserPortal'),
#);

$hashedSecrets = array(
    '/etc/vpn-config-api/config.yaml' => 'BasicAuthentication',
    '/etc/vpn-server-api/config.yaml' => 'Users',
);

$plainSecrets = array(
    '/etc/vpn-user-portal/config.yaml' => array('VpnConfigApi', 'VpnServerApi'),
    '/etc/vpn-admin-portal/config.yaml' => array('VpnServerApi', 'VpnConfigApi'),
);

try {
    if (3 > $argc) {
        throw new Exception(
            sprintf('SYNTAX: %s [apiUser] [apiSecret]', $argv[0])
        );
    }
    $apiUser = $argv[1];
    $apiSecret = $argv[2];
    $apiSecretHash = password_hash($apiSecret, PASSWORD_DEFAULT);

    foreach ($hashedSecrets as $configFile => $section) {
        $yamlFile = new YamlFile($configFile);
        $configData = $yamlFile->readConfig();
        $configData[$section] = array($apiUser => $apiSecretHash);
        $yamlFile->writeConfig($configData);
    }

    foreach ($plainSecrets as $configFile => $section) {
        $yamlFile = new YamlFile($configFile);
        $configData = $yamlFile->readConfig();
        foreach ($section as $s) {
            $configData[$s]['serviceUser'] = $apiUser;
            $configData[$s]['servicePass'] = $apiSecret;
        }
        $yamlFile->writeConfig($configData);
    }
} catch (Exception $e) {
    echo $e->getMessage().PHP_EOL;
    exit(1);
}
