---
title: Client Compatibility
description: List of Supported VPN Clients
category: documentation
---

This document describes a number of VPN clients that can be used to connect to 
the VPN service.

# Offical Applications

Official applications are available on most platforms. These are optimized for
working with the VPN software. The official applications are made available 
with two brand names:

* [eduVPN](https://eduvpn.org/): if you are part of the 
  research and education community and your institution is running the eduVPN 
  service;
* [Let's Connect!](https://letsconnect-vpn.org/) everyone else outside this 
  community, or when you run your own server, or someone else runs it for you.

The eduVPN applications only allow you to choose your organization from a 
curated list. The Let's Connect! applications allow you to specify a domain of
the VPN server to connect to.

The benefit of the official applications is that they will make it much easier 
for the end user to configure the VPN, and will make sure the VPN keeps 
working in case configuration updates are required for connecting to the VPN. 
The other applications may require manual configuration downloads through the 
user portal to be able to keep using the VPN.

A full list of official applications is available, including the changelogs: 

* [eduVPN](https://app.eduvpn.org/)
* [Let's Connect!](https://app.letsconnect-vpn.org/)

## Windows

* [eduVPN](https://app.eduvpn.org/windows/eduVPNClient_latest.exe)
* [Let's Connect!](https://app.letsconnect-vpn.org/windows/LetsConnectClient_latest.exe)

## Android

* [eduVPN](https://play.google.com/store/apps/details?id=nl.eduvpn.app) ([APK](https://app.eduvpn.org/android/eduvpn-latest.apk))
* [Let's Connect!](https://play.google.com/store/apps/details?id=org.letsconnect_vpn.app) ([APK](https://app.letsconnect-vpn.org/android/LetsConnect-latest.apk))

## macOS 

* [eduVPN](https://apps.apple.com/app/eduvpn-client/id1317704208?mt=12)
* [Let's Connect!](https://apps.apple.com/app/lets-connect-vpn/id1486810037?mt=12)

## iOS

* [eduVPN](https://itunes.apple.com/nl/app/eduvpn-client/id1292557340?mt=8)
* [Let's Connect!](https://itunes.apple.com/app/lets-connect-vpn/id1449261843?mt=8)

## Linux

* [eduVPN](https://python-eduvpn-client.readthedocs.io/en/master/)
* Let's Connect! (_not yet available_)

**NOTE**: see below for Linux support. The eduVPN/Let's Connect! application 
will only work properly if NetworkManager works properly with `tls-crypt` on 
your system! If not, you can use the manual instructions further down.

# Other Applications

In addition to the official applications, you can also use any OpenVPN 
compatible client on the platform of your choice. Some of the more popular ones
will be discussed below.

As long as as the VPN client is based on OpenVPN >= 2.4 or OpenVPN 3 it should
be possible to make it work.

## Windows 

* [OpenVPN Community client](https://openvpn.net/index.php/open-source/downloads.html)
  * Choose "Installer, Windows Vista and later";
  * Make sure you have the installer from the 2.4 release, e.g. 
    `openvpn-install-2.4.6-I602.exe`;
  * Keep your version updated, there may be (security) releases from time to time!

1. Install the OpenVPN Community client
2. (Optionally) read the documentation 
   [here](https://github.com/OpenVPN/openvpn-gui/);
3. Start OpenVPN (a Desktop icon is created automatically);
4. Import the downloaded configuration by right clicking on OpenVPN's tray icon and choosing "Import".

_NOTE_: OpenVPN will automatically start on Windows start-up, it will _not_ 
automatically connect!

## macOS

Download [tunnelblick](https://tunnelblick.net/). Make sure you use OpenVPN 
2.4 in tunnelblick! You can modify this in the settings if required. Read the 
[Quick Start Guide](https://tunnelblick.net/czQuick.html).

## Android

Install 
[OpenVPN for Android](https://play.google.com/store/apps/details?id=de.blinkt.openvpn), 
also available via 
[F-Droid](https://f-droid.org/repository/browse/?fdid=de.blinkt.openvpn).

The proprietary 
[OpenVPN Connect](https://play.google.com/store/apps/details?id=net.openvpn.openvpn) 
can also be used. See the OpenVPN Connect 
[FAQ](https://docs.openvpn.net/docs/openvpn-connect/openvpn-connect-android-faq.html).

## iOS

Install 
[OpenVPN Connect](https://itunes.apple.com/us/app/openvpn-connect/id590379981). 
A 
[FAQ](https://docs.openvpn.net/docs/openvpn-connect/openvpn-connect-ios-faq.html) 
is available.

You may want to enable `Seamless tunnel (iOS8+)` in the OpenVPN Settings. It 
will try to keep the VPN tunnel active as much as possible. See the FAQ for 
more details.
     
## Linux

The following table lists Linux distribution support when using 
NetworkManager's OpenVPN plugin and manual configuration.

On Fedora/Red Hat Enterprise Linux/CentOS you need to install the package
`NetworkManager-openvpn-gnome`. On Red Hat Enterprise Linux/CentOS you MUST 
first enable the [EPEL](https://fedoraproject.org/wiki/EPEL) repository!

On Debian/Ubuntu you need to install the `network-manager-openvpn-gnome` 
package. If you are using KDE you only need to install the 
`network-manager-openvpn` package.

See the instructions below on how to get the VPN working manually.

| Distribution            | NetworkManager | Manual | Remarks                                                                                                       |
| ----------------------- | -------------- | -------| ------------------------------------------------------------------------------------------------------------- |
| Debian 8                | no             | no     | Uses OpenVPN 2.3                                                                                              |
| Debian 9                | yes*           | yes    | `network-manager-openvpn` >= 1.2.10 required for `tls-crypt` support. A backport MUST be installed, see below |
| Debian 10               | yes            | yes    | -                                                                                                             |
| Ubuntu 16.04 LTS        | no             | no     | Uses OpenVPN 2.3                                                                                              |
| Ubuntu 18.04 LTS        | yes*           | yes    | [DNS leak](https://bugs.launchpad.net/ubuntu/+source/network-manager/+bug/1796648)                            |
| Kubuntu 18.04 LTS       | yes*           | yes    | KDE's VPN import does NOT work, use `nmcli connection import type openvpn file <file.ovpn>` from Konsole      |
| Ubuntu 18.10            | yes            | yes    | -                                                                                                             | 
| Ubuntu 19.04            | yes            | yes    | -                                                                                                             | 
| CentOS 7                | yes            | yes    | -                                                                                                             |
| Fedora 30, 31           | yes            | yes    | -                                                                                                             |

For Debian 8 and Ubuntu 16.04 LTS, an OpenVPN 
[repository](https://community.openvpn.net/openvpn/wiki/OpenvpnSoftwareRepos)
is available with a more up to date version of OpenVPN. This may be sufficient
to make the VPN work manually as described below, however, this was NOT tested.

On Debian 9, a _backport_ of `network-manager-openvpn` exists to make 
`tls-crypt` work. In order to install this, add the following line to 
`/etc/apt/sources.list`:

    deb http://deb.debian.org/debian stretch-backports main contrib non-free

Then install/update the relevant package:

    $ sudo apt update
    $ sudo apt -t stretch-backports install network-manager-openvpn-gnome

This will upgrade all required packages as well. You may need to reboot or 
restart NetworkManager.

### Configuration

Find your country in the [list of eduVPN servers](https://status.eduvpn.org/)
and download a configuration file from the server. If you want to use an
eduVPN server in a different country, you have to use the official
[eduvpn-client](https://python-eduvpn-client.readthedocs.io/en/master/) as
international authentication is currently only available through the API.

To import the resulting ovpn file into NetworkManager, use the `nmcli` command:

    $ nmcli conn import type openvpn file eduVPN_institute.ovpn

### Split Tunnel

If you do _not_ want to route all traffic over the VPN, you need to manually
specify this in NetworkManager. By default, NetworkManager will try to send
all traffic over the VPN, whether or not the servers indicates the VPN should
not be used as a default gateway.

When editing the VPN configuration, under the IPv4 and IPv6 tabs you can 
select "Use this connection only for resources on its network", this way it
will honor the pushed routes.

### Manual

To start OpenVPN manually, we assume below that you downloaded an OpenVPN 
configuration file through the user portal, e.g. 
`https://vpn.example.org/vpn-user-portal/`.

    $ sudo openvpn --config vpn.example.org_internet_20180101.ovpn

**NOTE**: The DNS servers will NOT be updated by running OpenVPN like this! See
instructions below for dealing with this automatically.

### Debian 9

Install the OpenVPN package:

    $ sudo apt install openvpn resolvconf

Copy your configuration file to `/etc/openvpn/client`. Make sure you give it 
the extension `.conf`! 

    $ sudo cp vpn.example.org_internet_20180101.ovpn \
        /etc/openvpn/client/vpn.example.org_internet_20180101.conf

Modify the configuration file, and add the following lines to it:

    script-security 2
    up /etc/openvpn/update-resolv-conf
    down /etc/openvpn/update-resolv-conf

Now start the OpenVPN service:

    $ sudo systemctl start openvpn-client@vpn.example.org_internet_20180101

### CentOS 7 / Red Hat Enterprise Linux 7

Install the OpenVPN package, make sure 
[EPEL](https://fedoraproject.org/wiki/EPEL) is enabled:

    $ sudo yum -y install openvpn

Copy your configuration file to `/etc/openvpn/client`. Make sure you give it 
the extension `.conf`! 

    $ sudo cp vpn.example.org_internet_20180101.ovpn \
        /etc/openvpn/client/vpn.example.org_internet_20180101.conf

Copy DNS update scripts to `/etc/openvpn` and modify the permissions:

    $ sudo cp /usr/share/doc/openvpn-*/contrib/pull-resolv-conf/client.* /etc/openvpn/
    $ sudo chmod 0755 /etc/openvpn/client.*

Modify the configuration file, and add the following lines to it:

    script-security 2
    up /etc/openvpn/client.up
    down /etc/openvpn/client.down

Now start the OpenVPN service:

    $ sudo systemctl start openvpn-client@vpn.example.org_internet_20180101
