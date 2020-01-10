<?php

// *** Source Formatting
// $ php-cs-fixer fix --rules @Symfony version_info.php
//
// *** Cron
// $ crontab -l
// @hourly	/usr/bin/php /home/fkooman/version_info.php > /var/www/html/fkooman/version_info.html.tmp && mv /var/www/html/fkooman/version_info.html.tmp /var/www/html/fkooman/version_info.html

// set this to the latest version of vpn-user-portal
// @see https://github.com/eduvpn/vpn-user-portal/releases
$latestVersion = '2.1.4';

// discovery files
$discoFiles = [
    'secure_internet' => 'https://static.eduvpn.nl/disco/secure_internet.json',
    'institute_access' => 'https://static.eduvpn.nl/disco/institute_access.json',
];

// other servers not part of any discovery file
$otherServerList = [
    'https://eduvpn.fyrkat.no/',
    'https://vpn.tuxed.net/',
    'https://vpn-dev.tuxed.net/',
    'https://meko.eduvpn.nl/',
    'https://vpn.spoor.nu/',
    'https://pi-vpn.tuxed.net/',
    'https://dia.eduroam.de/',
];

/**
 * @param string $serverHeaderKey
 *
 * @return string|null
 */
function determineOsRelease($serverHeaderKey)
{
    foreach (['CentOS', 'Debian', 'Fedora', 'Red Hat Enterprise Linux'] as $osRelease) {
        if (false !== strpos($serverHeaderKey, $osRelease)) {
            return $osRelease;
        }
    }

    return null;
}

$lastError = null;
set_error_handler(function ($errno, $errstr, $errfile, $errline) use (&$lastError) {
    $lastError = $errstr;
});

$streamContext = stream_context_create(
    [
        'http' => [
            'timeout' => 5,
        ],
    ]
);

$serverList = [];
// extract the "base_uri" from all discovery files
foreach ($discoFiles as $serverType => $discoFile) {
    if (!array_key_exists($serverType, $serverList)) {
        $serverList[$serverType] = [];
    }
    if (false === $discoJson = @file_get_contents($discoFile, false, $streamContext)) {
        continue;
    }
    $discoData = json_decode($discoJson, true);
    foreach ($discoData['instances'] as $serverInstance) {
        $serverList[$serverType][] = $serverInstance['base_uri'];
    }
}
// add the other servers to the list as well
$serverList['other'] = $otherServerList;

// now retrieve the info.json file from all servers
$serverInfoList = [];
foreach ($serverList as $serverType => $serverList) {
    foreach ($serverList as $baseUri) {
        $serverHost = parse_url($baseUri, PHP_URL_HOST);
        $hasIpFour = checkdnsrr($serverHost, 'A');
        $hasIpSix = checkdnsrr($serverHost, 'AAAA');
        $serverInfo = [
            'v' => null,
            'h' => $serverHost,
            'hasIpFour' => $hasIpFour,
            'hasIpSix' => $hasIpSix,
            'osRelease' => null,
            'serverType' => $serverType,
            'errMsg' => null,
        ];
        if (false === $infoJson = @file_get_contents($baseUri.'info.json', false, $streamContext)) {
            // find error
            $serverInfo['errMsg'] = $lastError;
            $lastError = null;
        } else {
            // we were able to obtain "info.json"
            $infoData = json_decode($infoJson, true);
            $serverInfo['v'] = array_key_exists('v', $infoData) ? $infoData['v'] : '?';

            // figure out the "Server"
            $serverHeaderString = null;
            if (isset($http_response_header)) {
                // we got the response header...
                foreach ($http_response_header as $responseHeader) {
                    if (0 === stripos($responseHeader, 'Server: ')) {
                        $serverInfo['osRelease'] = determineOsRelease($responseHeader);
                    }
                }
            }
        }
        $serverInfoList[$baseUri] = $serverInfo;
    }
}

$dateTime = new DateTime();
?>
<!DOCTYPE html>

<html lang="en-US" dir="ltr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>eduVPN Server Info</title>
    <style>
body {
    font-family: sans-serif;
    max-width: 50em;
    margin: 1em auto;
    color: #444;
}

code {
    font-size: 125%;
}

h1 {
    text-align: center;
}

table {
    border: 1px solid #ccc;
    width: 100%;
    border-collapse: collapse;
}

table th, table td {
    padding: 0.8em 0.5em;
}

table thead th {
    text-align: left;
}

table tbody tr:nth-child(odd) {
    background-color: #f8f8f8;
}

p, sup {
    font-size: 85%;
}

a {
    color: #444;
}

span.error {
    color: darkred;
}

span.success {
    color: darkgreen;
}

span.fade {
    color: lightgray;
}

span.awesome {
    color: lightgreen;
}

span.warning {
    color: darkorange;
}

footer {
    margin-top: 1em;
    font-size: 85%;
    color: #888;
    text-align: center;
}
    </style>
</head>
<body>
<h1>eduVPN Server Info</h1>
<p>The current <span class="success">STABLE</span> release is <?=$latestVersion; ?>.</p>
<table>
<thead>
    <tr>
        <th></th>
        <th>Server FQDN</th>
        <th>Version</th>
        <th>OS</th>
    </tr>
</thead>
<tbody>
<?php foreach ($serverInfoList as $baseUri => $serverInfo): ?>
    <tr>
        <td>
<?php if ('secure_internet' === $serverInfo['serverType']): ?>
            <span title="Secure Internet">🌍</span>
<?php elseif ('institute_access' === $serverInfo['serverType']): ?>
            <span title="Institute Access">🏛️</span>
<?php else: ?>
            <span title="Alien">👽</span>
<?php endif; ?>
        </td>
        <td>
            <a href="<?=$baseUri; ?>"><?=$serverInfo['h']; ?></a>
<?php if ($serverInfo['hasIpFour']): ?>
                <sup><span class="success" title="IPv4">4</span></sup>
<?php else: ?>
                <sup><span class="warning" title="No IPv4">4</span></sup>
<?php endif; ?>
<?php if ($serverInfo['hasIpSix']): ?>
                <sup><span class="success" title="IPv6">6</span></sup>
<?php else: ?>
                <sup><span class="warning" title="No IPv6">6</span></sup>
<?php endif; ?>
        </td>
        <td>
<?php if (null === $serverInfo['v']): ?>
<?php if (null !== $serverInfo['errMsg']): ?>
            <span class="error" title="<?=htmlentities($serverInfo['errMsg']); ?>">Error</span>
<?php else: ?>
            <span class="error">Error</span>
<?php endif; ?>
<?php else: ?>
<?php if ('?' === $serverInfo['v']): ?>
            <span class="warning">?</span>
<?php elseif (0 === strnatcmp($serverInfo['v'], $latestVersion)): ?>
            <span class="success"><?=$serverInfo['v']; ?></span>
<?php elseif (0 > strnatcmp($serverInfo['v'], $latestVersion)): ?>
            <span class="warning"><?=$serverInfo['v']; ?></span>
<?php else: ?>
            <span class="awesome"><?=$serverInfo['v']; ?></span>
<?php endif; ?>
<?php endif; ?>
        </td>
        <td>
<?php if (null === $serverInfo['osRelease']): ?>
            <span class="fade">Unknown</span>
<?php else: ?>
            <span><?=$serverInfo['osRelease']; ?></span>
<?php endif; ?>
        </td>
    </tr>
<?php endforeach; ?>
</tbody>
</table>
<p>The version <span class="warning">?</span> means the eduVPN component 
<code>vpn-user-portal</code> is older than version 
<a href="https://github.com/eduvpn/vpn-user-portal/blob/v2/CHANGES.md#214-2019-12-10">2.1.4</a>, 
the first release reporting the version. When the version is 
<span class="error">Error</span>, it means the server could not be reached, or 
there was problem establishing the (TLS) connection.
</p>
<footer>
Generated on <?=$dateTime->format(DateTime::ATOM); ?>
</footer>
</body>
</html>
