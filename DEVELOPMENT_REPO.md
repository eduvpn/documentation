# Development Repositories

**NOTE**: do this ONLY on your testing machines!

## CentOS

    $ cat << 'EOF' > /etc/yum.repos.d/eduVPN-development.repo
    [eduVPN-development]
    name=eduVPN Development Packages (EL 7)
    baseurl=https://repo.tuxed.net/eduVPN/v2/rpm/epel-7-$basearch
    gpgcheck=1
    gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
    EOF

## Fedora

    $ cat << 'EOF' > /etc/yum.repos.d/eduVPN-development.repo
    [eduVPN-development]
    name=eduVPN Development Packages (Fedora $releasever)
    baseurl=https://repo.tuxed.net/eduVPN/v2/rpm/fedora-$releasever-$basearch
    gpgcheck=1
    gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
    EOF
    
## Debian

On your Debian server:

    $ curl https://debian-vpn-builder.tuxed.net/repo/debian.key | sudo apt-key add

Replace `buster` with your version, can also be `stretch` (Debian 9) or 
`bullseye` (Debian 11).

    $ echo 'deb https://debian-vpn-builder.tuxed.net/repo buster main' | sudo tee -a /etc/apt/sources.list.d/eduVPN.list
