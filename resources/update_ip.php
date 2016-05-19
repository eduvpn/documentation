<?php

/**
 * Update the IP address configuration of vpn-server-api.
 *
 * IPv4:
 * Random value for the second and third octet, e.g: 10.53.129.0/24
 *
 * IPv6:
 * The IPv6 address is generated according to RFC 4193 (Global ID), it results 
 * in a /48 network.
 *
 * The addresses are written to /etc/vpn-server-api/pools.yaml
 */
require_once '/usr/share/php/fkooman/Config/autoload.php';
require_once '/usr/share/php/random_compat/autoload.php';

use fkooman\Config\YamlFile;

try {
    if (2 !== $argc) {
        throw new Exception('please specify the external interface');
    }

    $extIf = $argv[1];
    $v4 = sprintf('10.%s.%s.0/24', hexdec(bin2hex(random_bytes(1))), hexdec(bin2hex(random_bytes(1))));
    $v6 = sprintf('fd%s:%s:%s::/48', bin2hex(random_bytes(1)), bin2hex(random_bytes(2)), bin2hex(random_bytes(2)));

    echo sprintf('IPv4 CIDR  : %s', $v4).PHP_EOL;
    echo sprintf('IPv6 prefix: %s', $v6).PHP_EOL;

    $yamlFile = new YamlFile('/etc/vpn-server-api/pools.yaml');
    $configData = $yamlFile->readConfig();
    $configData['pools']['default']['range'] = $v4;
    $configData['pools']['default']['range6'] = $v6;
    # enable NAT
    $configData['pools']['default']['useNat'] = true;
    $configData['pools']['default']['extIf'] = $extIf;

    $yamlFile->writeConfig($configData);
} catch (Exception $e) {
    echo sprintf('ERROR: %s', $e->getMessage()).PHP_EOL;
    exit(1);
}
