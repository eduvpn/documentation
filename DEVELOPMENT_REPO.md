# Development Repositories

**NOTE**: do this ONLY on your testing machines!

## CentOS

    $ cat << 'EOF' > /etc/yum.repos.d/eduVPN-dev.repo
    [eduVPN-dev]
    name=eduVPN Development Packages (EL 7)
    baseurl=https://repo.tuxed.net/eduVPN/dev/rpm/epel-7-$basearch
    gpgcheck=1
    gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
    EOF

## Fedora

    $ cat << 'EOF' > /etc/yum.repos.d/eduVPN-dev.repo
    [eduVPN-dev]
    name=eduVPN Development Packages (Fedora $releasever)
    baseurl=https://repo.tuxed.net/eduVPN/dev/rpm/fedora-$releasever-$basearch
    gpgcheck=1
    gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
    EOF
    
## Debian

On your Debian server:

```
$ curl https://repo.tuxed.net/fkooman+repo@tuxed.net.asc | sudo apt-key add
$ echo "deb https://repo.tuxed.net/eduVPN/dev/deb $(/usr/bin/lsb_release -cs) main" | sudo tee -a /etc/apt/sources.list.d/eduVPN.list
```
