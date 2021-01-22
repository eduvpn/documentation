---
title: Raspberry Pi
description: Run a VPN server on your Raspberry Pi
category: advanced
---

# VPN Server on your Raspberry Pi

Because, why not. When developing technology, what use is it when you can't 
run it on the smallest and cheapest of devices? Why do we always need the 
latest and greatest to run anything? If you write software and it does NOT 
run on a Raspberry Pi with ease, you are doing something wrong ;-)

I tested this last on a Raspberry Pi 3B+ and Fedora 33 (aarch64) on 2021-01-21 
and all works fine. Currently **ONLY** packages for Fedora 33 are available.

**NOTE**: the Raspberry Pi 4 does **NOT** work yet as of this time 
(2021-01-21), wait for upstream Fedora to support it first! See 
[this](https://fedoraproject.org/wiki/Architectures/ARM/Raspberry_Pi#Raspberry_Pi_4).

# Getting Started

So, the first step is to find your Raspberry Pi 3B+ and get ready! Most of the
steps here are not specific to the VPN server, but just getting Fedora up and 
running, and up to date! 

Download the latest "Fedora Minimal" image from 
[here](https://alt.fedoraproject.org/alt/) make sure you look under the 
"ARM **aarch64** Architecture" section. The download will be a `raw.xz` file.

Full instructions for installing Fedora on the Pi can be found 
[here](https://fedoraproject.org/wiki/Architectures/ARM/Raspberry_Pi). I'll 
repeat the important steps below.

I used this command to create the SD card for the Pi on my laptop running 
Fedora:

    $ sudo arm-image-installer --image=Fedora-Minimal-33-1.3.aarch64.raw.xz --resizefs --target=rpi3 --media=/dev/mmcblk0

Make sure you specify the `--resizefs` option to "grow" the file system to fill
your SD card.

The Wiki linked to above has instructions for other platforms as well.

You need to boot this image, configure the network, install all software 
updates and enable (remote) SSH login if you prefer. It is a little bit easier 
and you don't need a keyboard/mouse attached to your Pi anymore. If you want to 
use WiFi, it DOES work out of the box on at least Fedora >= 32, but you need to 
configure it through the CLI as mentioned on the Wiki. The "installer" does not 
support it. First walk through the setup "wizard". Make sure you either create 
an account with "Administrator" permissions, or set a root password.

To configure WiFi if you don't have an ethernet connection:

    $ sudo nmcli device wifi connect "Your SSID" --ask

After connecting to the network, install all updates:
    
    $ sudo dnf -y --refresh update

Set the hostname to the name you want to give your VPN server:

    $ sudo hostnamectl set-hostname vpn.example.org

This concludes setting up Fedora on your Pi. Make sure everything works as 
expected and **reboot** before attempting to install the VPN software. Make 
sure your network connection is still working before continuing.

# Installing the VPN server

This is the easy part. Follow the instructions [here](DEPLOY_FEDORA.md), make
sure you enable the development repository when you call `deploy_fedora.sh`:

    # VPN_DEV_REPO=1 ./deploy_fedora.sh

After you are done with this, all should be fine as if you performed the 
installation on any other Fedora server.

## CA 

After installation, you probably want to switch away from using RSA for your 
VPN client and certificates for performance reasons, look 
[here](SECURITY.md#ca) on how do that, and 
[here](https://www.tuxed.net/fkooman/blog/openvpn_modern_crypto_part_ii.html) 
for why :)
