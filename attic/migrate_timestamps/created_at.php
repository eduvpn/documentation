<?php

require 'vendor/autoload.php';

use fkooman\X509\CertParser;

#$dbFile = __DIR__ . '/configurations.sqlite';
$dbFile = '/var/lib/vpn-user-portal/configurations.sqlite';
#$easyRsa = __DIR__ .'/easy-rsa/keys';
$easyRsa = '/var/lib/vpn-config-api/easy-rsa/keys';

$prefix = '';

$db= new PDO(
    sprintf('sqlite://%s', $dbFile)
);

$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$stmt = $db->prepare(
    sprintf(
        'SELECT user_id, name, created_at FROM %s WHERE created_at = 0',
        $prefix.'config'
    )
);
$stmt->execute();
$results = $stmt->fetchAll();
foreach($results as $result) {
    $certName = $easyRsa . '/' . $result['user_id'] . '_' . $result['name'] . '.crt';
	$certParser = CertParser::fromPemFile($certName);
	$createdAt = $certParser->getNotValidBefore();
    
    $stmt = $db->prepare(
        sprintf(
            'UPDATE %s SET created_at = :created_at WHERE user_id = :user_id AND name = :name',
            $prefix.'config'
        )
    );
    $stmt->bindValue(':user_id', $result['user_id'], PDO::PARAM_STR);
    $stmt->bindValue(':name', $result['name'], PDO::PARAM_STR);
    $stmt->bindValue(':created_at', $createdAt, PDO::PARAM_INT);
    $stmt->execute();
    echo $stmt->rowCount() . PHP_EOL;

//    echo $result['user_id'] . '_' . $result['name'] . ' DB: ' . $result['created_at'] . ' CERT: ' . $createdAt . PHP_EOL;
}

// get the 'not before' time from the certificate


