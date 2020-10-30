# Development Repositories

**NOTE**: do this ONLY on your testing machines!

## CentOS

    $ cat << 'EOF' > /etc/yum.repos.d/LC-master.repo
    [LC-master]
    name=VPN Packages (EL $releasever)
    baseurl=https://vpn-builder.tuxed.net/repo/master/epel-7-$basearch
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
    
## Debian

On your Debian server:

    $ curl https://debian-vpn-builder.tuxed.net/repo/debian.key | sudo apt-key add

Replace `buster` with your version, can also be `stretch` (Debian 9) or 
`bullseye` (Debian 11).

    $ echo 'deb https://debian-vpn-builder.tuxed.net/repo buster main' | sudo tee -a /etc/apt/sources.list.d/eduVPN.list
