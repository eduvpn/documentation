# Repositories

This page will tell you everything about the (production) package repositories
for eduVPN / Let's Connect!.

This page will reflect always the most up to date configuration and keys that
are required for using the packages.

# Debian

## Keys

Owner   | Fingerprint                                          | Expires
------- | ---------------------------------------------------- | ----------
fkooman | `21D9 2D75 0EFB 4AF8 EC72  E9E9 8004 C0D4 E38C 85C3` | 2025-08-16

The key can be found 
[here](https://repo.eduvpn.org/v2/deb/debian-20200817.key). To
install it:

```
$ curl -O https://repo.eduvpn.org/v2/deb/debian-20200817.key
$ gpg --import-options show-only --import debian-20200817.key
$ sudo cp debian-20200817.key /etc/apt/trusted.gpg.d/eduVPN_v2.asc
```

## Config

The repository configuration is done in 
`/etc/apt/sources.list.d/eduVPN_v2.list`, add the following line there 
depending on the version of Debian you are using.

### Debian 10

```
deb https://repo.eduvpn.org/v2/deb buster main
```

### Debian 11

```
deb https://repo.eduvpn.org/v2/deb bullseye main
```

# CentOS

## Keys

Owner   | Fingerprint                                          | Expires
------- | ---------------------------------------------------- | ----------
fkooman | `99AF 412F BBA0 BF17 92EE  1F41 BAC1 8982 20FB 8A35` | 2026-04-18

The key can be found 
[here](https://repo.eduvpn.org/v2/rpm/centos%2B20210419%40eduvpn.org.asc). To
install it:

```
$ curl -O https://repo.eduvpn.org/v2/rpm/centos%2B20210419%40eduvpn.org.asc
$ gpg --import-options show-only --import centos%2B20210419%40eduvpn.org.asc
$ sudo rpm --import centos%2B20210419%40eduvpn.org.asc
```

## Config

`/etc/yum.repos.d/eduVPN_v2.repo`

```
[eduVPN_v2]
name=eduVPN 2.x Packages (EL 7)
baseurl=https://repo.eduvpn.org/v2/rpm/centos+epel-7-$basearch
gpgcheck=1
enabled=1
```

# Fedora

## Keys

Owner   | Fingerprint                                          | Expires
------- | ---------------------------------------------------- | ----------
fkooman | `99AF 412F BBA0 BF17 92EE  1F41 BAC1 8982 20FB 8A35` | 2026-04-18

The key can be found 
[here](https://repo.eduvpn.org/v2/rpm/centos%2B20210419%40eduvpn.org.asc). To
install it:

```
$ curl -O https://repo.eduvpn.org/v2/rpm/centos%2B20210419%40eduvpn.org.asc
$ gpg --import-options show-only --import centos%2B20210419%40eduvpn.org.asc
$ sudo rpm --import centos%2B20210419%40eduvpn.org.asc
```

## Config

`/etc/yum.repos.d/eduVPN_v2.repo`

```
[eduVPN_v2]
name=eduVPN 2.x Packages (Fedora)
baseurl=https://repo.eduvpn.org/v2/rpm/fedora-$releasever-$basearch
gpgcheck=1
enabled=1
```
