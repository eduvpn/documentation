# Production Package Repositories

This page will tell you everything about the production package repositories 
for eduVPN / Let's Connect!.

This page will always reflect the most up to date configuration and keys that
are required for using the packages.

## Repository Key

Owner   | Fingerprint                                          | Expires
------- | ---------------------------------------------------- | ----------
fkooman | `F671 0CAA FBB4 7A8A 3EC9  1800 629D 7EE2 B63D DE73` | 2032-05-13

### PGP Key

[Download](resources/repo+v3@eduvpn.org.asc)

```
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEYoKbBhYJKwYBBAHaRw8BAQdAYqEfYQm8BFK1dC7dFbOQRoV+q47cB9i0gur8
z9Dg4820MGVkdVZQTiAzLnggUmVwbyBTaWduaW5nIEtleSA8cmVwbyt2M0BlZHV2
cG4ub3JnPoiZBBMWCgBBFiEE9nEMqvu0eoo+yRgAYp1+4rY93nMFAmKCmwYCGwMF
CRLMAwAFCwkIBwICIgIGFQoJCAsCBBYCAwECHgcCF4AACgkQYp1+4rY93nPy0QEA
2hsMIdl4M/rYC/xWjwlJMPdYhRumcsB4LPvpFCynV80A/iezye1QS+HbFvWLe35f
2fCzZPEXcfBj62wfeP3j+9EE
=3C81
-----END PGP PUBLIC KEY BLOCK-----
```

# Debian / Ubuntu

## Repository Key

```bash
$ curl https://repo.eduvpn.org/v3/deb/repo+v3@eduvpn.org.asc | sudo tee /etc/apt/trusted.gpg.d/repo+v3@eduvpn.org.asc
```

## Repository Config

```bash
echo "deb https://repo.eduvpn.org/v3/deb $(/usr/bin/lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/eduVPN_v3.list
```

# Fedora

## Repository Key

```bash
$ curl -O https://repo.eduvpn.org/v3/rpm/repo+v3@eduvpn.org.asc
$ sudo rpm --import repo+v3@eduvpn.org.asc
```

## Repository Config

Add the following to the file `/etc/yum.repos.d/eduVPN_v3.repo`:

```
[eduVPN_v3]
name=eduVPN 3.x Packages (Fedora $releasever)
baseurl=https://repo.eduvpn.org/v3/rpm/fedora-$releasever-$basearch
gpgcheck=1
enabled=1
```

# Enterprise Linux

## Repository Key

```bash
$ curl -O https://repo.eduvpn.org/v3/rpm/repo+v3@eduvpn.org.asc
$ sudo rpm --import repo+v3@eduvpn.org.asc
```

## Repository Config

Add the following to the file `/etc/yum.repos.d/eduVPN_v3.repo`:

```
[eduVPN_v3]
name=eduVPN 3.x Packages (EL9)
baseurl=*REPLACE ME, SEE BELOW*
gpgcheck=1
enabled=1
```

Set the `baseurl` with the value from the column, depending on your exact OS:

| OS            | `baseurl`                                            |
| ------------- | ---------------------------------------------------- |
| Rocky Linux 9 | `https://repo.eduvpn.org/v3/rpm/rocky+epel-9-x86_64` |
| AlmaLinux 9   | `https://repo.eduvpn.org/v3/rpm/alma+epel-9-x86_64`  |
