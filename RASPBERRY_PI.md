# VPN Server on your Raspberry Pi

**NOTE**: as of 2019-11-25 I still need to test this with Fedora 31 on my Pi!

Because, why not. When developing technology, what use is it when you can't 
run it on the smallest and cheapest of devices? Why do we always need the 
latest and greatest to run anything? If you write software and it does NOT 
run on a Raspberry Pi with ease, you are doing something wrong.

I'l be attempting this on a Raspberry Pi 3B+ and Fedora 31 (aarch64).

# Getting Started

So, the first step is to find your Raspberry Pi 3+ and get ready! Most of the
steps here are not specific to the VPN server, but just getting Fedora up and 
running, and up to date! 

Download the latest "Fedora Minimal" image from 
[here](https://alt.fedoraproject.org/alt/). It will be a `raw.xz` file.

Full instructions for installing Fedora on the Pi can be found 
[here](https://fedoraproject.org/wiki/Architectures/ARM/Raspberry_Pi). I'll 
repeat the important steps below.

For example, on 2019-11-25, I used this command to create the SD card for the 
Pi:

    $ sudo arm-image-installer --image=Fedora-Minimal-31-1.9.aarch64.raw.xz --resizefs --target=rpi3 --media=/dev/mmcblk0

Make sure you specify the `--resizefs` option to "grow" the filesystem to fill
your SD card.

You need to boot this image, configure the network, install all software updates 
and enable (remote) SSH login if you prefer. It is a little bit easier and 
you don't need a keyboard/mouse attached to your Pi anymore.

This concludes setting up Fedora on your Pi. Make sure everything works as 
expected.

# Installing the VPN server

This is the easy part. Follow the instructions [here](DEPLOY_FEDORA.md), make
sure you enable the development repository when you call `deploy_fedora.sh`:

    # VPN_DEV_REPO=1 ./deploy_fedora.sh

After you are done with this, all should be fine!
