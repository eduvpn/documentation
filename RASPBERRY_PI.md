# Raspberry Pi Deployment

Because, why not. When developing technology, what use is it when you can't 
run it on the smallest and cheapest of devices? Why do we always need the 
latest and greatest to run anything? If you write software and it does NOT 
run on a Raspberry Pi with ease, you are doing something wrong ;-)

## Downloading Fedora

Download the latest Fedora image, at the time of writing this is Fedora 37
for _aarch64_.

* [Fedora Minimal](https://download.fedoraproject.org/pub/fedora-secondary/releases/37/Spins/aarch64/images/Fedora-Minimal-37-1.7.aarch64.raw.xz)

You can check [here](https://alt.fedoraproject.org/alt/) for the latest image,
make sure you download the "Minimal" image.

## Installing Fedora

So, the first step is to find your Raspberry Pi 3B+ or 4 and get ready! Most of 
the steps here are not specific to the VPN server, but just getting Fedora up 
and running, and up to date! 

Full instructions for installing Fedora on the Pi can be found 
[here](https://fedoraproject.org/wiki/Architectures/ARM/Raspberry_Pi). I'll 
repeat the important steps below.

I used this command to create the SD card for the Pi on my laptop running 
Fedora.

To write to SD-card, for USB disk you would use something like 
`--media=/dev/sdb`:

```bash
$ sudo arm-image-installer --image=Fedora-Minimal-37-1.7.aarch64.raw.xz --resizefs --target=rpi3 --media=/dev/mmcblk0
```

**NOTE**: for the Raspberry Pi 4, use `--target=rpi4`!

Make sure you specify the `--resizefs` option to "grow" the file system to fill
your SD card/USB disk.

The Wiki linked to above has instructions for other platforms as well.

You need to boot this image, configure the network, install all software 
updates and enable (remote) SSH login if you prefer. It is a little bit easier 
and you don't need a keyboard/mouse attached to your Pi anymore. If you want to 
use WiFi, it DOES work out of the box with the Raspberry Pi 3B+ on at least 
Fedora, but you need to configure it through the CLI as mentioned on the Wiki. 
The "installer" does not support it. First walk through the setup "wizard". 
Make sure you either create an account with "Administrator" permissions, or set 
a root password.

To configure WiFi if you don't have an ethernet connection:

```bash
$ sudo nmcli device wifi connect "Your SSID" --ask
```

After connecting to the network, install all updates:
    
```bash
$ sudo dnf -y --refresh update
```

Set the hostname to the name you want to give your VPN server:

```bash
$ sudo hostnamectl set-hostname vpn.example.org
```

This concludes setting up Fedora on your Pi. Make sure everything works as 
expected and **reboot** before attempting to install the VPN software. Make 
sure your network connection is still working before continuing.

# Installing the VPN server

This is the easy part. Follow the instructions [here](DEPLOY_FEDORA.md), make
sure you enable the development repository when you call `deploy_fedora.sh`:

```bash
# USE_DEV_REPO=y ./deploy_fedora.sh
```

After you are done with this, all should be fine as if you performed the 
installation on any other Fedora server.
