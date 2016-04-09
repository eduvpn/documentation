<?php

require_once '/usr/share/php/fkooman/Config/autoload.php';
require_once '/usr/share/php/random_compat/autoload.php';

use fkooman\Config\YamlFile;

// IPv4
$v4 = sprintf('10.%s.%s.0/24', hexdec(bin2hex(random_bytes(1))), hexdec(bin2hex(random_bytes(1))));
$v6 = sprintf('fd%s:%s:%s::/48', bin2hex(random_bytes(1)), bin2hex(random_bytes(2)), bin2hex(random_bytes(2)));

echo sprintf('IPv4 CIDR  : %s', $v4).PHP_EOL;
echo sprintf('IPv6 prefix: %s', $v6).PHP_EOL;

$yamlFile = new YamlFile('/etc/vpn-server-api/ip.yaml');
$configData = $yamlFile->readConfig();
$configData['v4']['range'] = $v4;
$configData['v6']['prefix'] = $v6;
$yamlFile->writeConfig($configData);
