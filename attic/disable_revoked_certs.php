<?php

require_once '/usr/share/vpn-ca-api/src/fkooman/VPN/CA/autoload.php';
#require_once '/var/www/vpn-ca-api/vendor/autoload.php';

use fkooman\VPN\CA\IndexParser;

#$indexPath = '/var/lib/vpn-ca-api/easy-rsa/keys/index.txt'; # EasyRSA2
$indexPath = '/var/lib/vpn-ca-api/easy-rsa/pki/index.txt'; # EasyRSA3
#$indexPath = '/var/www/vpn-ca-api/data/easy-rsa/pki/index.txt'; # Development

$disabledDir = '/var/lib/vpn-server-api/common_names/disabled';
#$disabledDir = '/var/www/vpn-server-api/data/common_names/disabled';

// create dir if it does not yet exists
@mkdir($disabledDir, 0751, true);

// find the revoked CNs 
$i = new IndexParser($indexPath);
$certList = $i->getCertList();

$disableCommonNames = [];
foreach ($certList as $certEntry) {
    if ('R' === $certEntry['state']) {
        $commonName = sprintf('%s_%s', $certEntry['user_id'], $certEntry['name']);
        $disableCommonNames[] = [
            'cn' => $commonName,
            'exp' => $certEntry['exp'],
        ];
    }
}

// create disable files for these CNs
foreach ($disableCommonNames as $commonName) {
    $disabledFile = sprintf('%s/%s', $disabledDir, $commonName['cn']);
    // write the revoked time in the disabled file
    echo $disabledFile.' ('.$commonName['exp'].')'.PHP_EOL;
    file_put_contents($disabledFile, $commonName['exp']);
}
