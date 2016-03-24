<?php

require_once '/usr/share/php/fkooman/Config/autoload.php';
require_once '/usr/share/php/random_compat/autoload.php';

use fkooman\Config\YamlFile;

$vupvca = bin2hex(random_bytes(16));
$vupvsa = bin2hex(random_bytes(16));
$vapvca = bin2hex(random_bytes(16));
$vapvsa = bin2hex(random_bytes(16));
$vsavca = bin2hex(random_bytes(16));

#$vupvca = 'XXX-vpn-user-portal/vpn-ca-api-XXX';
#$vupvsa = 'XXX-vpn-user-portal/vpn-server-api-XXX';
#$vapvca = 'XXX-vpn-admin-portal/vpn-ca-api-XXX';
#$vapvsa = 'XXX-vpn-admin-portal/vpn-server-api-XXX';
#$vsavca = 'XXX-vpn-server-api/vpn-ca-api-XXX';

$configFiles = [
    'vpn-user-portal' => [
        'config' => '/etc/vpn-user-portal/config.yaml',
        'remoteApi' => [
            'vpn-ca-api' => $vupvca,
            'vpn-server-api' => $vupvsa,
        ],
    ],
    'vpn-admin-portal' => [
        'config' => '/etc/vpn-admin-portal/config.yaml',
        'remoteApi' => [
            'vpn-ca-api' => $vapvca,
            'vpn-server-api' => $vapvsa,
        ],
    ],
    'vpn-server-api' => [
        'config' => '/etc/vpn-server-api/config.yaml',
        'remoteApi' => [
            'vpn-ca-api' => $vsavca,
        ],
        'api' => [
            'vpn-user-portal' => $vupvsa,
            'vpn-admin-portal' => $vapvsa,
        ],
    ],
    'vpn-ca-api' => [
        'config' => '/etc/vpn-ca-api/config.yaml',
        'api' => [
            'vpn-user-portal' => $vupvca,
            'vpn-admin-portal' => $vapvca,
            'vpn-server-api' => $vsavca,
        ],
    ],
];

try {
    foreach ($configFiles as $tokenId => $c) {
        $yamlFile = new YamlFile($c['config']);
        $configData = $yamlFile->readConfig();
        if (array_key_exists('remoteApi', $c)) {
            // remoteApi
            foreach ($c['remoteApi'] as $k => $v) {
                $configData['remoteApi'][$k]['token'] = $v;
            }
        }
        if (array_key_exists('api', $c)) {
            // api
            foreach ($c['api'] as $k => $v) {
                $configData['api'][$k]['token'] = $v;
            }
        }
        $yamlFile->writeConfig($configData);
    }
} catch (Exception $e) {
    echo $e->getMessage().PHP_EOL;
    exit(1);
}
