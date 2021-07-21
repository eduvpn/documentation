---
title: Traceable NAT
description: Make NAT users tracable using a static iptables configuration
category: advanced
author: Jørn Åne de Jong (Uninett)
---

# Traceable NAT

## Introduction

When using NAT, it is hard to identify the user behind an action, because every uses has the same outgoing IP address.
A solution to this could be Netflow, but that requires Netflow to be installed on every eduVPN host, which can be a hassle.

Instead, this document proposes a solution with rudimentary implementation, where every internal IPv4 address
is mapped to a limited range of port numbers for outgoing traffic.  With this, any user can be traced in two ways:

1. Incident reports will typically include the source port number used
2. If Netflow is used outside the eduVPN host, this will log the port number used by the eduVPN server


## How it works

The administrator must run a script that will generate iptables rules for the VPN node.  This can be done at the same time that `vpn-maint-apply-changes` is run.  Afterwards, the firewall must be reloaded, which would cause users' connections inside the tunnel to be reset, so the script only restarts the firewall when it's necessary.

Every time the script is run, it will check if the current iptables rules in /etc/iptables/rules.v4 are identical to the desired rules,
if they are, the script does nothing.  If they are not, it will update the rules in the file and restart the firewall.  When it does this, it will write the rules as a new file and keep the old file so that IP/port mappings can always be retrieved.  The old firewall files have a UNIX timestamp in their filename, so when you must investigate an incident, you can find how the firewall was configured at the time of that incident, and which port number was used by which internal IP address.


## Set up

This is only tested on Debian, and probably won't work on CentOS/Fedora.

Copy the `vpn-generate-natfw.php` file in this repository.

	install -m755 vpn-generate-natfw.php /usr/bin/vpn-generate-natfw

Now you must generate the iptables configuration and save it. If you want to test before you write, run

	vpn-generate-natfw -n

If you are happy with the result, you can write it by running without arguments

	vpn-generate-natfw

If you want to see what other options are available

	vpn-generate-natfw --help

That's all!  If you have any procedure where you run `vpn-server-node-server-config` or `vpn-maint-apply-changes` automatically,
you might consider running `vpn-generate-natfw` at the same time.  Never run `vpn-generate-natfw` with `-f` (force) from cron/systemd timers!


## "Ephemeral Ports"

```
$ sysctl net.ipv4.ip_local_port_range
net.ipv4.ip_local_port_range = 32768	60999
```

These are the ports used by the OS itself to give to services that open 
connections. So you want your VPN client port range to stay out of this range.

There's also `net.ipv4.ip_local_reserved_ports` which won't be used.

These options also apply to IPv6.

Sources: 
* https://superuser.com/questions/1118735/how-are-source-ports-determined-and-how-can-i-force-it-to-use-a-specific-port
* https://unix.stackexchange.com/questions/279157/ipv6-ephemeral-port-range

## Tracing an incident

In order to trace a user, you need three bits of information

* Date+time
* IP addresses involved
* Source port number

### 1. Find the firewall configuration that was active when the incident happened.

You need to have the date in UNIX timestamp format. Run

	date +%s -d '2020/12/26 13:37:42'

You will get a number, such as `1608986262`

### 2. Find the matching firewall configuration

Get a list of all firewall configurations

	ls -1 /etc/iptables/

You will see multiple files in the format `rules.v4.1608946501` with different numbers.
You must find the **highest** number that is still lower than the UNIX timestamp.

### 3. Find the internal IP address

Display the firewall rules

	less /etc/iptables/rules.v4.1608946501

You will see a lot of lines such as

	-A POSTROUTING -s 192.168.101.2 -p tcp -j SNAT --to-source 192.0.2.1:65280-65535
	-A POSTROUTING -s 192.168.101.2 -p udp -j SNAT --to-source 192.0.2.1:65280-65535
	-A POSTROUTING -s 192.168.101.3 -p tcp -j SNAT --to-source 192.0.2.1:65024-65279
	-A POSTROUTING -s 192.168.101.3 -p udp -j SNAT --to-source 192.0.2.1:65024-65279
	-A POSTROUTING -s 192.168.101.4 -p tcp -j SNAT --to-source 192.0.2.1:64768-65023
	-A POSTROUTING -s 192.168.101.4 -p udp -j SNAT --to-source 192.0.2.1:64768-65023
	-A POSTROUTING -s 192.168.101.5 -p tcp -j SNAT --to-source 192.0.2.1:64512-64767
	-A POSTROUTING -s 192.168.101.5 -p udp -j SNAT --to-source 192.0.2.1:64512-64767
	-A POSTROUTING -s 192.168.101.6 -p tcp -j SNAT --to-source 192.0.2.1:64256-64511
	-A POSTROUTING -s 192.168.101.6 -p udp -j SNAT --to-source 192.0.2.1:64256-64511

Port ranges are shown at the end of the line. Scroll with the arrow keys or PgUp/PgDown and find the line that matches your source port number.
You have now found the internal IPv4 address that was involved in the incident.  This internal IP address (on the left) can be matched to a user through the eduVPN portal (webinterface).

# Example Script

`vpn-generate-natfw.php`:

```php
#!/usr/bin/php
<?php

// conf, faster/better to manually set the IPv4 address
$publicIp = trim(shell_exec('ip addr | grep \'state UP\' -A2 | tail -n1 | awk \'{print $2}\' | cut -f1  -d\'/\''));
$maxPort = 65535;
$minPort = 1280;

/*
 * eduVPN - End-user friendly VPN.
 *
 * Copyright: 2021, Jørn Åne de Jong, Uninett AS
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Some parts are copied from the eduVPN project by The Commons Conservancy
 * These parts are AGPL-3 licensed.  They are clearly marked with // BEGIN snippet and // END snippet
 */

if ($argc > 1 && (in_array('-h', $argv) || in_array('--help', $argv))) {
	fwrite(STDERR, $argv[0] . ' [-f] [-n] [-v] [-w filename] [-c command]' . PHP_EOL);
	fwrite(STDERR, "\t-f\tForce overwriting existing file (not needed if existing file is a symlink)" . PHP_EOL);
	fwrite(STDERR, "\t-n\tDry run (output file to stdout)" . PHP_EOL);
	fwrite(STDERR, "\t-v\tVerbose (also output if nothing changed)" . PHP_EOL);
	fwrite(STDERR, "\t-w filename\tWrite to filename, default /etc/iptables/rules.v4" . PHP_EOL);
	fwrite(STDERR, "\t-c command\tCommand to run if a new file was written, default service netfilter-persistent restart" . PHP_EOL);
	exit;
}

require_once '/usr/share/php/LC/Node/autoload.php';
$baseDir = '/usr/share/vpn-server-node';

use LC\Common\Config;
use LC\Common\HttpClient\CurlHttpClient;
use LC\Common\HttpClient\ServerClient;
use LC\Common\ProfileConfig;
use LC\Node\OpenVpn;

class IP extends LC\Node\IP {
	function getAllHosts() {
		// Works only for IPv4 but that's okay,
		// we don't support NATv6.
		// I would call $this->requireIPv4() but it's private.
		$counter = $this->getNumberOfHosts() - 1;
		$addr = ip2long($this->getFirstHost());
		while( $counter-- ) {
			yield long2ip( ++$addr );
		}
	}
	function split($networkCount) {
		// Make sure we return instances of ourself, not the parent
		return array_map(function($ip) {
				return new self($ip->__toString());
			}, parent::split($networkCount));
	}
}

$networks = [];
try {
// BEGIN snippet copy from /usr/bin/vpn-server-node-server-config
	$configFile = sprintf('%s/config/config.php', $baseDir);
	$config = Config::fromFile($configFile);

	$vpnUser = $config->requireString('vpnUser', 'openvpn');
	$vpnGroup = $config->requireString('vpnGroup', 'openvpn');

	$vpnConfigDir = sprintf('%s/openvpn-config', $baseDir);
	$serverClient = new ServerClient(
			new CurlHttpClient($config->requireString('apiUser'), $config->requireString('apiPass')),
			$config->requireString('apiUri')
		);

	$profileIdDeployList = $config->requireArray('profileList', []);
// END snippet copy from /usr/bin/vpn-server-node-server-config

// BEGIN snippet copy from /usr/share/php/LC/Node/OpenVpn.php
	$profileList = $serverClient->getRequireArray('profile_list');
	// filter out the profiles we do not want on this node
	if (0 !== \count($profileIdDeployList)) {
		foreach (array_keys($profileList) as $profileId) {
			if (!\in_array($profileId, $profileIdDeployList, true)) {
				unset($profileList[$profileId]);
			}
		}
	}

	foreach($profileList as $profileConfigData) {
		$profileConfig = new ProfileConfig(new Config($profileConfigData));
		$processCount = \count($profileConfig->vpnProtoPorts());
		$range = new IP($profileConfig->range());
		$splitRange = $range->split($processCount);
		$networks = array_merge($networks, $splitRange);
	}
// END snippet copy from /usr/share/php/LC/Node/OpenVpn.php
} catch (Exception $e) {
	fwrite(STDERR, 'Error: ' . $e->getMessage() . PHP_EOL);
	exit (1);
}

$addresses = 0;
$privateNetworks = [];
foreach($networks as $network) {
	if (substr($network, 0, 3) === '10.' // 10/8
		// 172.16/12
		|| substr($network, 0, 7) === '172.16.'
		|| substr($network, 0, 7) === '172.17.'
		|| substr($network, 0, 7) === '172.18.'
		|| substr($network, 0, 7) === '172.19.'
		|| substr($network, 0, 7) === '172.20.'
		|| substr($network, 0, 7) === '172.21.'
		|| substr($network, 0, 7) === '172.22.'
		|| substr($network, 0, 7) === '172.23.'
		|| substr($network, 0, 7) === '172.24.'
		|| substr($network, 0, 7) === '172.25.'
		|| substr($network, 0, 7) === '172.26.'
		|| substr($network, 0, 7) === '172.27.'
		|| substr($network, 0, 7) === '172.28.'
		|| substr($network, 0, 7) === '172.29.'
		|| substr($network, 0, 7) === '172.30.'
		|| substr($network, 0, 7) === '172.31.'
		// 192.168/16
		|| substr($network, 0, 8) === '192.168.'
		// 100.64/10
		|| substr($network, 0, 7) === '100.64.'
		|| substr($network, 0, 7) === '100.65.'
		|| substr($network, 0, 7) === '100.66.'
		|| substr($network, 0, 7) === '100.67.'
		|| substr($network, 0, 7) === '100.68.'
		|| substr($network, 0, 7) === '100.69.'
		|| substr($network, 0, 5) === '100.7'
		|| substr($network, 0, 5) === '100.8'
		|| substr($network, 0, 5) === '100.9'
		|| (substr($network, 0, 6) === '100.10' && substr($network, 0, 7) !== '100.10.')
		|| (substr($network, 0, 6) === '100.11' && substr($network, 0, 7) !== '100.11.')
		|| substr($network, 0, 7) === '100.120.'
		|| substr($network, 0, 7) === '100.121.'
		|| substr($network, 0, 7) === '100.122.'
		|| substr($network, 0, 7) === '100.123.'
		|| substr($network, 0, 7) === '100.124.'
		|| substr($network, 0, 7) === '100.125.'
		|| substr($network, 0, 7) === '100.126.'
		|| substr($network, 0, 7) === '100.127.'
	) {
		// -1 to remove the gw address
		$addresses += $network->getNumberOfHosts() - 1;
		$privateNetworks[] = $network;
	}
}
if (!$privateNetworks) {
	fwrite(STDERR, 'Error: There are no private networks in ' . implode(', ', $networks) . PHP_EOL);
	exit (1);
}

$portsPerClient = floor(($maxPort-$minPort)/$addresses);
$candidate = 1;
for($candidate = 1; $portsPerClient > $candidate; $candidate = $candidate << 1) {};
$portsPerClient = $candidate >> 1;

// Buffer output, so we don't write if there's an error
$output = '';
$output .= '# Generated by vpn-generate-natfw on ' . date('D M d H:i:s Y') . PHP_EOL;
$output .= "# NAT ports per client: $portsPerClient" . PHP_EOL;
$output .= "*nat" . PHP_EOL;
$output .= ":PREROUTING ACCEPT [0:0]" . PHP_EOL;
$output .= ":INPUT ACCEPT [0:0]" . PHP_EOL;
$output .= ":POSTROUTING ACCEPT [0:0]" . PHP_EOL;
$output .= ":OUTPUT ACCEPT [0:0]" . PHP_EOL;

$port = $maxPort + 1;
$output .= "-A POSTROUTING -p icmp -j SNAT --to-source $publicIp" . PHP_EOL;
foreach($privateNetworks as $network) foreach($network->getAllHosts() as $ip) {
	$max = $port - 1;
	$min = $port - $portsPerClient;
	$port = $min;
	$output .= "-A POSTROUTING -s $ip -p tcp -j SNAT --to-source $publicIp:$min-$max" . PHP_EOL;
	$output .= "-A POSTROUTING -s $ip -p udp -j SNAT --to-source $publicIp:$min-$max" . PHP_EOL;
}
$output .= "COMMIT" . PHP_EOL;
$output .= "*filter" . PHP_EOL;
$output .= ":INPUT ACCEPT [0:0]" . PHP_EOL;
$output .= ":FORWARD ACCEPT [0:0]" . PHP_EOL;
$output .= ":OUTPUT ACCEPT [0:0]" . PHP_EOL;
$output .= "COMMIT" . PHP_EOL;

if (in_array('-n', $argv)) {
	$file = null;
} else {
	$file = '/etc/iptables/rules.v4';
}
$command = 'service netfilter-persistent restart';
for($i = 0; $i < sizeof($argv); $i++) {
	if ($argv[$i] === '-w') {
		$file = $argv[++$i];
		if ($file === null) {
			fwrite(STDERR, 'Error: Invalid file specified with -w' . PHP_EOL);
		}
	}
	if ($argv[$i] === '-c') {
		$command = $argv[++$i];
		if ($command === null) {
			fwrite(STDERR, 'Error: Invalid command specified with -c' . PHP_EOL);
		}
	}
}

if (null === $file) {
	echo $output;
} else {
	$original = @file_get_contents($file);
	if (preg_replace('/# Generated by vpn-generate-natfw on .*/', '', $original)
		=== preg_replace('/# Generated by vpn-generate-natfw on .*/', '', $output)) {
		if ($argc > 1 && in_array('-v', $argv)) {
			fwrite(STDERR, 'Success: file is unchanged: ' . $file . PHP_EOL);
		}
	} else {
		if (!in_array('-f', $argv) && file_exists($file) && !is_link($file)) {
			fwrite(STDERR, 'Error: Output file already exists ' . $file . PHP_EOL);
			fwrite(STDERR, 'Hint: Use -f one time to overwrite it, or simply delete it' . $file . PHP_EOL);
			exit (1);
		}
		$writeFile = $file . '.' . time();
		if (file_put_contents($writeFile, $output)) {
			fwrite(STDERR, 'Success: Wrote new ruleset to ' . $writeFile . PHP_EOL);
			@unlink($file);
			if (symlink($writeFile, $file)) {
				fwrite(STDERR, 'Success: Updated symlink ' . $file . PHP_EOL);
				passthru($command, $return);
				if ($return) {
					fwrite(STDERR, 'Failure: ' . $command . PHP_EOL);
				} else {
					fwrite(STDERR, 'Success: ' . $command . PHP_EOL);
				}
				exit ($return);
			}
		} else {
			fwrite(STDERR, 'Error: Unable to write to output file ' . $writeFile . PHP_EOL);
			exit (1);
		}
	}
}
```
