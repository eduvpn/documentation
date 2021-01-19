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

## Config

The repository configuration is done in `/etc/apt/sources.list.d/eduVPN.list`,
add the following line there depending on the version of Debian you are using.

### Debian 9

```
deb https://repo.eduvpn.org/v2/deb stretch main
```

### Debian 10

```
deb https://repo.eduvpn.org/v2/deb buster main
```

# CentOS

## Keys

Owner   | Fingerprint                                          | Expires
------- | ---------------------------------------------------- | ----------
fkooman | `1B50 FE64 0B1A 36AC F8F9  3117 1ACB 2EDE AA79 31B2` | 2021-05-01

## Config

`/etc/yum.repos.d/eduVPN.repo`

```
[eduVPN-v2]
name=eduVPN (EL)
baseurl=https://repo.eduvpn.org/v2/rpm/epel-7-$basearch
gpgcheck=1
enabled=1
```

# Fedora

## Keys

Owner   | Fingerprint                                          | Expires
------- | ---------------------------------------------------- | ----------
fkooman | `1B50 FE64 0B1A 36AC F8F9  3117 1ACB 2EDE AA79 31B2` | 2021-05-01

## Config

`/etc/yum.repos.d/eduVPN.repo`

```
[eduVPN-v2]
name=eduVPN (Fedora)
baseurl=https://repo.eduvpn.org/v2/rpm/fedora-$releasever-$basearch
gpgcheck=1
enabled=1
```
