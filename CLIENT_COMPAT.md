# Introduction

This document describes a number of VPN clients to that can be used to connect
to the VPN service.

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
The other applications may require manual configuration downloads to be able
to keep using the VPN.

## Windows

* [eduVPN](https://app.eduvpn.org/windows/eduVPNClient_latest.exe)
* [Let's Connect!](https://app.letsconnect-vpn.org/windows/LetsConnectClient_latest.exe)

## Android

* [eduVPN](https://play.google.com/store/apps/details?id=nl.eduvpn.app) [APK](https://app.eduvpn.org/android/eduvpn-latest.apk)
* [Let's Connect!](https://play.google.com/store/apps/details?id=org.letsconnect_vpn.app) [APK](https://app.letsconnect-vpn.org/android/LetsConnect-latest.apk)

## iOS

* [eduVPN](https://itunes.apple.com/nl/app/eduvpn-client/id1292557340?mt=8)
* Let's Connect! (_not yet available_)

On iOS we do not currently have a "full" application. You will also need to 
download [OpenVPN Connect](https://itunes.apple.com/us/app/openvpn-connect/id590379981?mt=8) 
to be able to connect to the VPN. The eduVPN/Let's Connect! application will 
handle configuration downloads and then offer to import the configuration in 
the OpenVPN Connect application. We are currently working on improving the 
situation!

## macOS 

* [eduVPN](https://app.eduvpn.org/mac/eduVPN_latest.dmg)
* Let's Connect! (_not yet available_)

## Linux

* [eduVPN](https://python-eduvpn-client.readthedocs.io/en/master/)
* Let's Connect! (_not yet available_)

# Other Applications

In addition to the official applications, you can also use any OpenVPN 
compatible client on the platform of your choice. Some of the more popular ones
will be discussed below.

As mentioned above, if you have the choice, we recommend you to use the 
official applications if possible.

Indirectly, the client compatibility is controlled through the `tlsProtection` 
option. On new deployments, the `tlsProtection` option is set to `tls-crypt`, 
supporting only the latest version(s) of OpenVPN.

| `tlsProtection` | Compatiblity                                                          | Allowed Cipher(s)            | Routing "Fix" |
| --------------- | --------------------------------------------------------------------- | ---------------------------- | ------------- |
| `tls-crypt`     | >= 2.4, 3, [TunnelKit](https://github.com/keeshux/TunnelKit)          | `AES-256-GCM`                | no            |
| `tls-auth`      | >= 2.3, 3  TunnelKit                                                  | `AES-256-CBC`, `AES-256-GCM` | yes           |
| `false`         | >= 2.3, 3, TunnelKit, [PIA](https://github.com/pia-foss/tunnel-apple) | `AES-256-GCM`                | no            |

In addition, when `tlsProtection` is set to `tls-auth`, routes are pushed to 
the client to fix IPv6 (default gateway) routing over the VPN tunnel, this is 
needed, because OpenVPN 2.3 does not support the IPv6 default gateway flag. On
OpenVPN 2.4 those extra routes are ignored.

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

Download [tunnenblick](https://tunnelblick.net/). Make sure you use OpenVPN 
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

The following is a list of Linux distribution support when using 
NetworkManager's OpenVPN plugin with a default deployment of the VPN server.

| Distribution     | Works | Remarks                                                              |
| ---------------- | ----- | -------------------------------------------------------------------- |
| CentOS 7         | no    | `NetworkManager-openvpn` >= 1.2.10 required for `tls-crypt` support [RHBZ](https://bugzilla.redhat.com/show_bug.cgi?id=1520214) |
| Fedora 28        | yes   | -                                                                    |
| Ubuntu 16.04 LTS | no    | Uses OpenVPN 2.3
| Ubuntu 18.04 LTS | yes   | [DNS leak](https://github.com/systemd/systemd/issues/7182#issuecomment-350335001) |
| Debian 8         | no    | Uses OpenVPN 2.3                                                     |
| Debian 9         | no    | `network-manager-openvpn` >= 1.2.10 required for `tls-crypt` support |

To make all Linux clients work, you can set `tlsProtection` to `tls-auth`, but
this will break existing configurations, unless you use the eduVPN/Let's 
Connect! client.

In order to install the NetworkManager OpenVPN plugin, you can install the 
package `NetworkManager-openvpn-gnome` on Fedora/CentOS/Red Hat Enterprise 
Linux and the package `network-manager-openvpn-gnome` on Debian/Ubuntu.

### Command Line

You can either start OpenVPN manually, or enable it using `systemctl`. We 
assume below that you downloaded an OpenVPN configuration file through the 
user portal, e.g. `https://vpn.example.org/vpn-user-portal/`.

#### Manually

    $ sudo openvpn --config vpn.example.org_internet_20180101.ovpn

Please note that your DNS servers will NOT be updated by running OpenVPN like
this! 

#### systemd

Copy your configuration file to `/etc/openvpn/client`. Make sure you give it 
the extension `.conf`! 

    $ sudo cp vpn.example.org_internet_20180101.ovpn \
        /etc/openvpn/client/vpn.example.org_internet_20180101.conf

On Debian, modify the configuration file, and add the following lines to it:

    script-security 2
    up /etc/openvpn/update-resolv-conf
    down /etc/openvpn/update-resolv-conf

On Fedora / CentOS you need to copy some scripts to `/etc/openvpn` and modify 
the permissions:

    $ sudo cp /usr/share/doc/openvpn/contrib/pull-resolv-conf/client.* /etc/openvpn/
    $ sudo chmod 0755 /etc/openvpn/client.*

Add the following lines to your OpenVPN configuration file:

    script-security 2
    up /etc/openvpn/client.up
    down /etc/openvpn/client.down

Now you can start/enable OpenVPN, but immediately and at boot:

    $ sudo systemctl enable --now openvpn-client@vpn.example.org_internet_20180101
