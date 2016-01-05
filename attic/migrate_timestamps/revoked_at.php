<?php

#$dbFile = __DIR__ . '/configurations.sqlite';
$dbFile = '/var/lib/vpn-user-portal/configurations.sqlite';
#$easyRsa = __DIR__ .'/easy-rsa/keys';
$easyRsa = '/var/lib/vpn-config-api/easy-rsa/keys';

$prefix = '';

$db= new PDO(
    sprintf('sqlite://%s', $dbFile)
);

$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);


$row = 1;
if (($handle = fopen($easyRsa . '/index.txt', "r")) !== FALSE) {
    while (($data = fgetcsv($handle, 1000, "\t")) !== FALSE) {
        $num = count($data);
        if(!empty($data[2])) {
            $cn = $data[5];
            preg_match('|CN=([^/]*)|', $cn, $matches);
            $cn = $matches[1];

            $f = 'ymdHis?';
            $datetime = DateTime::createFromFormat($f, $data[2]);//, new DateTimeZone(DateTimeZone::UTC));
            $ts = $datetime->getTimeStamp();
            list($userId, $name) = explode('_', $cn, 2);

//            echo $ts . ' ' . $datetime->format('Y-m-d H:i:s') . ' ' . $data[2] . ':' . $cn . ' ' .$userId . ' ' .$name . PHP_EOL;
        
    
            $stmt = $db->prepare(
                sprintf(
                    'UPDATE %s SET revoked_at = :revoked_at WHERE user_id = :user_id AND name = :name AND revoked_at = 0',
                    $prefix.'config'
                )
            );

            $stmt->bindValue(':user_id', $userId, PDO::PARAM_STR);
            $stmt->bindValue(':name', $name, PDO::PARAM_STR);
            $stmt->bindValue(':revoked_at', $ts, PDO::PARAM_INT);
            $stmt->execute();
            echo $stmt->rowCount() . PHP_EOL;

        }
    }
    fclose($handle);
}
?>

