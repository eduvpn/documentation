<?php

// *** Source Formatting
// $ php-cs-fixer fix --rules @Symfony version_info.php
//
// *** Cron
// $ crontab -l
// @hourly	/usr/bin/php /home/fkooman/version_info.php > /var/www/html/fkooman/version_info.html.tmp && mv /var/www/html/fkooman/version_info.html.tmp /var/www/html/fkooman/version_info.html

// set this to the latest version of vpn-user-portal
// @see https://github.com/eduvpn/vpn-user-portal/releases
$latestVersion = '2.2.1';

// discovery files
$discoFiles = [
    'secure_internet' => 'https://static.eduvpn.nl/disco/secure_internet.json',
    'institute_access' => 'https://static.eduvpn.nl/disco/institute_access.json',
];

// other servers not part of any discovery file
$otherServerList = [];
if (file_exists('other_server_list.txt')) {
    $otherBaseUriList = explode("\n", trim(file_get_contents('other_server_list.txt')));
    foreach ($otherBaseUriList as $otherBaseUri) {
        $otherServerList[] = [
            'base_uri' => $otherBaseUri,
            'display_name' => parse_url($otherBaseUri, PHP_URL_HOST),
            'support_contact' => [],
        ];
    }
}

/**
 * @param string $u
 *
 * @return string
 */
function getUrl($u, &$responseHeaders = [])
{
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $u);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTPS);
    curl_setopt(
        $ch,
        CURLOPT_HEADERFUNCTION,
        function ($ch, $headerString) use (&$responseHeaders) {
            $responseHeaders[] = $headerString;

            return strlen($headerString);
        }
    );

    if (false === $responseData = curl_exec($ch)) {
        $errorMessage = curl_error($ch);
        curl_close($ch);
        throw new RuntimeException('ERROR: '.$errorMessage);
    }
    curl_close($ch);

    return $responseData;
}

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

/**
 * @return string
 */
function getDisplayName(array $serverInstance)
{
    if (!array_key_exists('display_name', $serverInstance)) {
        return $serverInstance['base_uri'];
    }
    if (!is_array($serverInstance['display_name'])) {
        return $serverInstance['display_name'];
    }
    if (array_key_exists('en-US', $serverInstance['display_name'])) {
        return $serverInstance['display_name']['en-US'];
    }

    return array_values($serverInstance['display_name'])[0];
}

/**
 * @param string $uriStr
 *
 * @return string
 */
function removeUriPrefix($uriStr)
{
    if (0 === strpos($uriStr, 'tel:')) {
        return substr($uriStr, 4);
    }
    if (0 === strpos($uriStr, 'mailto:')) {
        return substr($uriStr, 7);
    }

    return $uriStr;
}

$serverList = [];
// extract the "base_uri" from all discovery files
foreach ($discoFiles as $serverType => $discoFile) {
    if (!array_key_exists($serverType, $serverList)) {
        $serverList[$serverType] = [];
    }

    try {
        $discoJson = getUrl($discoFile);
        $discoData = json_decode($discoJson, true);
        foreach ($discoData['instances'] as $serverInstance) {
            $serverList[$serverType][] = [
                'base_uri' => $serverInstance['base_uri'],
                'display_name' => getDisplayName($serverInstance),
                'support_contact' => array_key_exists('support_contact', $serverInstance) ? $serverInstance['support_contact'] : [],
            ];
        }
    } catch (RuntimeException $e) {
        // do nothing
    }
}

// add the other servers to the list as well
$serverList['other'] = $otherServerList;

// now retrieve the info.json file from all servers
$serverInfoList = [];
foreach ($serverList as $serverType => $serverList) {
    foreach ($serverList as $srvInfo) {
        $baseUri = $srvInfo['base_uri'];
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
            'displayName' => $srvInfo['display_name'],
            'support_contact' => $srvInfo['support_contact'],
        ];
        try {
            $responseHeaderList = [];
            $infoJson = getUrl($baseUri.'info.json', $responseHeaderList);
            $infoData = json_decode($infoJson, true);
            $serverInfo['v'] = array_key_exists('v', $infoData) ? $infoData['v'] : '?';
            foreach ($responseHeaderList as $responseHeader) {
                if (0 === stripos($responseHeader, 'Server: ')) {
                    $serverInfo['osRelease'] = determineOsRelease($responseHeader);
                }
            }
        } catch (RuntimeException $e) {
            $serverInfo['errMsg'] = $e->getMessage();
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

small {
    font-size: 75%;
    color: #888;
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

ul {
    margin: 0;
    padding: 0 1em;
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
        <th>Support</th>
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
            <a href="<?=$baseUri; ?>"><?=$serverInfo['displayName']; ?></a> <small>[<?=$serverInfo['h']; ?>]</small>
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
            <span class="fade">?</span>
<?php else: ?>
            <span><?=$serverInfo['osRelease']; ?></span>
<?php endif; ?>
        </td>
        <td>
<?php if (0 !== count($serverInfo['support_contact'])): ?>
            <ul>
<?php foreach ($serverInfo['support_contact'] as $supportContact): ?>
            <li><a href="<?=$supportContact; ?>"><?=removeUriPrefix($supportContact); ?></a></li>
<?php endforeach; ?>
            </ul>
<?php else: ?>
            <span class="fade">?</span>
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
