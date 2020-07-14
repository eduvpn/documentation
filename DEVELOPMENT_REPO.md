---
title: Development Repository
description: Use the Development Repository on your VPN server
category: howto
---

# Development Repository

**NOTE**: run this ONLY on your testing machines!

## CentOS

    $ cat << 'EOF' > /etc/yum.repos.d/LC-master.repo
    [LC-master]
    name=VPN Packages (EL $releasever)
    baseurl=https://vpn-builder.tuxed.net/repo/master/epel-$releasever-$basearch
    gpgcheck=1
    gpgkey=https://vpn-builder.tuxed.net/repo/master/RPM-GPG-KEY-LC
    EOF

## Fedora

    $ cat << 'EOF' > /etc/yum.repos.d/LC-master.repo
    [LC-master]
    name=VPN Packages (Fedora $releasever)
    baseurl=https://vpn-builder.tuxed.net/repo/master/fedora-$releasever-$basearch
    gpgcheck=1
    gpgkey=https://vpn-builder.tuxed.net/repo/master/RPM-GPG-KEY-LC
    EOF
