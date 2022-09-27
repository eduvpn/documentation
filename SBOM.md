# Introduction

This page lists ALL software, including dependencies, of the _production_ 
releases of eduVPN / Let's Connect! It does _not_ include installation or
maintenance scripts.

It is an initial attempt to create an 
[SBOM](https://en.wikipedia.org/wiki/Software_supply_chain).

| Component       												     | Description                     | Branch | Language |
| ------------------------------------------------------------------ | ------------------------------- | ------ | -------- |
| [vpn-user-portal](https://git.sr.ht/~fkooman/vpn-user-portal)      | User Portal / API               | `v3`   | PHP      |
| [vpn-server-node](https://git.sr.ht/~fkooman/vpn-server-node)      | Node                            | `v3`   | PHP      |
| [php-secookie](https://git.sr.ht/~fkooman/php-secookie/)           | Cookie/session library          | `main` | PHP      |
| [php-oauth2-server](https://git.sr.ht/~fkooman/php-oauth2-server/) | OAuth 2.0 server                | `main` | PHP      |
| [vpn-daemon](https://git.sr.ht/~fkooman/vpn-daemon)                | Manages VPN connections on Node | `main` | Go       |
| [vpn-ca](https://git.sr.ht/~fkooman/vpn-ca)                        | X.509 Server/Client Cert CA     | `main` | Go       |

The only _additional_ dependency we have is the WireGuard library written 
in Go, [wgctrl-go](https://github.com/WireGuard/wgctrl-go) that is a 
dependency of `vpn-daemon`. The library itself has again a bunch of 
dependencies that we ignore and just _vendor_ in the `vpn-daemon`
releases.

What is also missing is the PHP autoloader that is used when packaging the 
software for Fedora and Enterprise Linux, and 
[phpab](https://github.com/theseer/Autoload) which is used both there and by 
the Debian/Ubuntu packages.