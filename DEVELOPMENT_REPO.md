# Development Repositories

**NOTE**: do this ONLY on your testing machines!

## eduVPN 2.x

### CentOS

    $ cat << 'EOF' > /etc/yum.repos.d/eduVPN_v2-dev.repo
    [eduVPN_v2-dev]
    name=eduVPN 2.x Development Packages (EL 7)
    baseurl=https://repo.tuxed.net/eduVPN/v2-dev/rpm/epel-7-$basearch
    gpgcheck=1
    gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
    EOF

### Fedora

    $ cat << 'EOF' > /etc/yum.repos.d/eduVPN_v2-dev.repo
    [eduVPN_v2-dev]
    name=eduVPN 2.x Development Packages (Fedora $releasever)
    baseurl=https://repo.tuxed.net/eduVPN/v2-dev/rpm/fedora-$releasever-$basearch
    gpgcheck=1
    gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
    EOF
    
### Debian

On your Debian server:

```
$ curl https://repo.tuxed.net/fkooman+repo@tuxed.net.asc | sudo tee /etc/apt/trusted.gpg.d/fkooman.asc
$ echo "deb https://repo.tuxed.net/eduVPN/v2-dev/deb $(/usr/bin/lsb_release -cs) main" | sudo tee -a /etc/apt/sources.list.d/eduVPN_v2-dev.list
```

## eduVPN 3.x

### CentOS

N/A

### Fedora

    $ cat << 'EOF' > /etc/yum.repos.d/eduVPN_v3-dev.repo
    [eduVPN_v3-dev]
    name=eduVPN 3.x Development Packages (Fedora $releasever)
    baseurl=https://repo.tuxed.net/eduVPN/v3-dev/rpm/fedora-$releasever-$basearch
    gpgcheck=1
    gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
    EOF
    
### Debian

N/A
