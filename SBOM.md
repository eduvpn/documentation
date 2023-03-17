# SBOM

This page lists ALL software, including dependencies, of the _production_ 
releases of eduVPN / Let's Connect! It does _not_ include installation or 
maintenance scripts, not components that we consider part of the operating 
system, e.g.: OpenVPN, WireGuard, Apache, PHP, Go, which we use without 
modification.

It is an initial attempt to create an 
[SBOM](https://en.wikipedia.org/wiki/Software_supply_chain).

| Component       												    | Description                     | Tag/Branch | Language | LoC*  |
| ----------------------------------------------------------------- | ------------------------------- | ---------- | -------- | ----- |
| [vpn-user-portal](https://git.sr.ht/~fkooman/vpn-user-portal)     | User Portal / API               | `3.3.0`    | PHP      | 12281 |
| [vpn-server-node](https://git.sr.ht/~fkooman/vpn-server-node)     | Node                            | `3.0.2`    | PHP      | 1028  |
| [php-secookie](https://git.sr.ht/~fkooman/php-secookie/)          | Cookie/session library          | `6.1.0`    | PHP      | 835   |
| [php-oauth2-server](https://git.sr.ht/~fkooman/php-oauth2-server) | OAuth 2.0 server                | `7.4.0`    | PHP      | 2169  |
| [vpn-daemon](https://git.sr.ht/~fkooman/vpn-daemon)               | Manages VPN connections on Node | `main`     | Go       | 380   |
| [vpn-ca](https://git.sr.ht/~fkooman/vpn-ca)                       | X.509 Server/Client Cert CA     | `main`     | Go       | 263   |
| [wgctrl-go](https://github.com/WireGuard/wgctrl-go)               | WireGuard Go Library            | `master`   | Go       | ?     |

We do not list the dependencies of `wgctrl-go`, there are many (indirect) ones. 
It is not exactly clear to me which ones are actually used. We _vendor_ 
`wgctrl-go` (and its dependencies) in the `vpn-daemon` releases, see the 
`make_release.sh` script in the `vpn-daemon` project.

We create Fedora / Enterprise Linux and Debian / Ubuntu packages. The 
packages are created using 
[builder.rpm](https://git.sr.ht/~fkooman/builder.rpm) and 
[nbuilder.deb](https://git.sr.ht/~fkooman/nbuilder.deb). The 
_package descriptions_ can be found by appending `.rpm` or `.deb` behind the 
repository name of the "Component" listed above.

What is also missing is the PHP autoloader that is used when packaging the 
software for Fedora and Enterprise Linux, and 
[phpab](https://github.com/theseer/Autoload) which is used both there and by 
the Debian/Ubuntu packages. We also omit the _development dependencies_, like 
PHPUnit for running unit tests.

`*` For PHP we use [phploc](https://github.com/sebastianbergmann/phploc) and 
look in the output for `NCLOC`. For Go code we use 
[cloc](https://github.com/AlDanial/cloc). All projects (except `wgctrl-go`) 
include a `Makefile` target `sloc` that can be used to reproduce these values. 

**Last Updated**: 2023-01-23
