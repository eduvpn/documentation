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
 * The addresses are written to /etc/vpn-server-api/%{HOSTNAME}/config.yaml
 */
require_once '/usr/share/php/random_compat/autoload.php';
require_once '/usr/share/php/Symfony/Component/Yaml/autoload.php';

use Symfony\Component\Yaml\Yaml;

try {
    if (3 !== $argc) {
        throw new RuntimeException('please specify the hostname and the external interface');
    }

    $hostName = $argv[1];
    $extIf = $argv[2];
    $v4 = sprintf('10.%s.%s.0/24', hexdec(bin2hex(random_bytes(1))), hexdec(bin2hex(random_bytes(1))));
    $v6 = sprintf('fd%s:%s:%s:%s::/60', bin2hex(random_bytes(1)), bin2hex(random_bytes(2)), bin2hex(random_bytes(2)), bin2hex(random_bytes(2) & hex2bin('fff0')));

    echo sprintf('IPv4 CIDR  : %s', $v4).PHP_EOL;
    echo sprintf('IPv6 prefix: %s', $v6).PHP_EOL;

    $configFile = sprintf('/etc/vpn-server-api/%s/config.yaml', $hostName);
    $configData = Yaml::parse(file_get_contents($configFile));

    $configData['vpnPools']['internet']['range'] = $v4;
    $configData['vpnPools']['internet']['range6'] = $v6;
    $configData['vpnPools']['internet']['extIf'] = $extIf;

    if (false === @file_put_contents($configFile, Yaml::dump($configData, 3))) {
        throw new RuntimeException(sprintf('unable to write "%s"', $configFile));
    }
} catch (Exception $e) {
    echo sprintf('ERROR: %s', $e->getMessage()).PHP_EOL;
    exit(1);
}
