## Introduction

**NOTE**: WireGuard functionality is **EXPERIMENTAL** and not available in 
any official VPN packages yet! Do NOT use in production!

It is available in the eduVPN/Let's Connect! 3.x development release.

## Requirements

WireGuard will only be supported on servers running Debian >= 11 and 
Fedora >= 34. Currently only Fedora 34 (x86_64) is being tested.

You can install the eduVPN 3.x development release on Fedora 34 using the 
`deploy_fedora_v3.sh` script instead of the `deploy_fedora.sh` script. That 
should set up a lot for you already.

## Configuration

You can add a profile to `/etc/vpn-user-portal/config.php` with the `vpnProto` 
set to `wireguard`. Most options apply both to OpenVPN and WireGuard.

## API

The WireGuard integration also exposes an API for use by apps. It works the 
same way as the existing API, protected using OAuth. This API is in a state of 
flux and will defintely change before being rolled out in production!

Check our [APIv3](API_V3.md) document on how to use it for obtaining WireGuard 
client configurations.

## Client

In the portal you can see the WireGuard client configuration file after 
selecting a WireGuard profile. You can copy/paste this in the WireGuard 
client on Windows and macOS. On Android and iOS you can scan the QR code. On
Linux you can import the configuration file like this. For example, save the
configuration snippet from the portal in a file called `wg3.conf` and do this:

    $ nmcli connection import type wireguard file wg3.conf

That should immediately make the VPN over WireGuard work. Test with for example
`http://v6.de`.

## TODO

- finish proper WG connection logging
- limit the number of configurations per user (also relevant for OpenVPN)
