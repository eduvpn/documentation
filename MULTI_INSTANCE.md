# Multi Instance

The software supports deploying various instances on one machine. This means
that one installation can host multiple VPN installations on multiple domains,
e.g. it can support both `https://vpn.foo.org/` and `https://vpn.bar.org`.

These instances are completely separated, they have their own configuration 
folders, their own data store and run their own OpenVPN processes.

**TBD**
