# Multi Pool Configurations

**THIS IS WORK IN PROGRESS, NOT SUPPORTED YET**

Instead of just supporting one "pool", it is possible to support multiple 
pools. For instance, one pool that allows users to safely browse the Internet
and one that allows for access to the institute's private network.

These can be configured separately.

# Default Configuration

    pools:
        default:
            name: Default Pool
            #listen: '::'
            hostName: vpn.example
            extIf: eth0
            useNat: true
            range: 10.42.42.0/24
            range6: 'fd00:4242:4242::/48'
            defaultGateway: true
            #routes: [10.10.0.0/16, 192.168.1.0/24, 'fd00:1234:5678:9999::/64']
            dns: [8.8.8.8, 8.8.4.4, '2001:4860:4860::8888', '2001:4860:4860::8844']
            twoFactor: false
            clientToClient: false
            enableLog: true

# Adding a Pool

The important line is the `listen` key. By default it will listen on all IP 
addresses for the UDP instances, which will not work in multi-pool 
configurations. In this case each pool needs its own dedicated IP address to 
listen on.

In the example we will have the public IP addresses `192.0.2.1` and `192.0.2.2` for
the pools.

    pools:
        default:
            name: Default Pool
            listen: 192.0.2.1
            hostName: default.vpn.example
            extIf: eth0
            useNat: true
            range: 10.42.42.0/24
            range6: 'fd00:4242:4242::/48'
            defaultGateway: true
            dns: [8.8.8.8, 8.8.4.4, '2001:4860:4860::8888', '2001:4860:4860::8844']

        office:
            name: Office
            listen: 192.0.2.2
            hostName: office.vpn.example
            extIf: eth1
            useNat: false
            range: 192.168.1.0/24
            range6: 'fd00:1234:5678::/48'
            defaultGateway: false
            routes: [192.168.5.0/24, 'fd00:4444:4444::/48']
            clientToClient: true
            twoFactor: true
            enableLog: true

The `office` pool here will not use NAT, will only push the two routes, will 
not push DNS and will allow traffic to be routed over the `eth1` interface, 
assuming it is connected to the office LAN.

It will also allow clients to reach each other, and enable Two-factor 
Authentication for which the user has to enroll in the user portal.

# Additional Configuration

The above supports connecting over IPv4 to UDP only. To restore TCP 
connectivity over IPv4 `/etc/sniproxy.conf` needs to be modified.

It currently has:

    listen 443 {
        proto tls
        fallback 127.42.0.1:1194
        table https_hosts
    }

This needs to be changed:

    listen 192.0.2.1:443 {
        proto tls
        fallback 127.42.0.1:1194
        table https_hosts
    }

    listen 192.0.2.2:443 {
        proto tls
        fallback 127.42.1.1:1194
        table https_hosts
    }

This makes everything work again for connecting over IPv4.

## IPv6

If you also want to allow connecting to the VPN service over IPv6, additional
configuration is required, both for TCP and UDP. We assume the public IPv6 
addresses for the VPN server are `2001:db8::192:0:2:1/64` and 
`2001:db8::192:0:2:2/64`.

### TCP

First add these to the existing configuration in `/etc/sniproxy.conf`:

    listen [2001:db8::192:0:2:1]:443 {
        proto tls
        fallback 127.42.0.1:1194
        table https_hosts
    }

    listen [2001:db8::192:0:2:2]:443 {
        proto tls
        fallback 127.42.1.1:1194
        table https_hosts
    }

### UDP 

**TODO**: document this better, also automatically start this on boot, check
performance impact, test this with various clients, ...

The UDP case is a bit more tricky. One can use `socat` like this:

    $ socat UDP6-LISTEN:1194,bind=[2001:db8::192:0:2:1] UDP4:192.0.2.1:1194
    $ socat UDP6-LISTEN:1195,bind=[2001:db8::192:0:2:1] UDP4:192.0.2.1:1195
    $ socat UDP6-LISTEN:1196,bind=[2001:db8::192:0:2:1] UDP4:192.0.2.1:1196

    $ socat UDP6-LISTEN:1194,bind=[2001:db8::192:0:2:2] UDP4:192.0.2.2:1194
    $ socat UDP6-LISTEN:1195,bind=[2001:db8::192:0:2:2] UDP4:192.0.2.2:1195
    $ socat UDP6-LISTEN:1196,bind=[2001:db8::192:0:2:2] UDP4:192.0.2.2:1196
