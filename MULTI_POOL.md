# Multi Pool

Every VPN [instance](MULTI_INSTANCE.md) supports multiple "pools". This means 
that every instance can host multiple "deployment scenarios". For instance 
there can be two pools, one for employees and one for network administrators. 
They can have completely different configurations, ACLs based on group 
membership and optionally two-factor authentication.

Below a configuration example is given for exactly this scenario. An 
organization has employees and administrators. The employees can access the VPN
to access the organization's resources, while the administrators can access 
additional networks to manage servers. The administrators are determined by the
ACL and have two-factor authentication enabled as to provide extra security.

We assume the instance is running as `https://vpn.example/` and was deployed 
using the provided deploy script.

**TODO**: create a deploy-like script to add a pool.

## Internet

The default [configuration](POOL_CONFIG.md) is called `internet` and routes all 
traffic from the client IP addresses using NAT over the external interface. The
current configuration can be found in 
`/etc/vpn-server-api/vpn.example/config.yaml`:

    vpnPools:
        internet:
            displayName: 'Internet Access'
            extIf: eth0
            hostName: vpn.example
            range: 10.0.0.0/24
            range6: 'fd00:4242:4242::/48'
            dns: [8.8.8.8, 8.8.4.4, '2001:4860:4860::8888', '2001:4860:4860::8844']

## Office

Now, we can add an additional pool here that is for employees wanting to access
the company network, but it is important to add the `listen` directive to the
`internet` pool. It must be a unique IP address per pool, that is reachable by 
clients:

    vpnPools:
        internet:
            ...
            listen: 192.0.2.1

        office:
            displayName: 'Office'
            extIf: eth1
            listen: 192.0.2.2
            hostName: office-vpn.example
            range: 192.168.5.0/24
            range6: 'fd00:1111:1111:1110::/60'
            useNat: false
            defaultGateway: false
            routes: [192.168.1.0/24, 192.168.2.0/24]

We assume here that `eth1` is connected to the office LAN and that the ranges
`192.168.1.0/24` and `192.168.2.0/24` are pushed to the client so they can 
reach the machines in the network.

It is also easy to add an [ACL](ACL.md) to the pool, or require 
[two-factor authentication](2FA.md). [More](POOL_CONFIG.md) configuration 
options are available.

# Deploy

In order to activate, new configuration files for the OpenVPN processes need
to be generated, the processes restarted and some other configuration changes
need to be made.

## OpenVPN

    $ su -c 'for F in `ls /etc/systemd/system/multi-user.target.wants/*openvpn*`; do B=`basename $F` ; systemctl disable $B ; done;'

    $ TODO stop old, disable old

    $ sudo vpn-server-api-server-config --instance vpn.example
    
    $ TODO enable new, start new

## Firewall

Generate the new firewall:

    $ sudo vpn-server-api-generate-firewall --install

Restart the firewall:

    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables

## sniproxy

It is no longer possible for sniproxy to listen on `0.0.0.0` as it is 
impossible to detect which OpenVPN connection over `TCP/443` belongs to which
pool, so sniproxy must also bind to the IP addresses as defined above. The 
default configuration:

    user sniproxy
    pidfile /var/run/sniproxy.pid

    listen 443 {
        proto tls
        fallback 127.42.101.100:1194
        table https_hosts
    }

    table https_hosts {
        vpn.example 127.42.101.100:8443
    }

The modification will look like this. Note the `listen` line where the IP 
address now matches the `listen` directive from the above pool config. In the
line with `fallback` the IP address used is the one on which the OpenVPN 
process listens. For the first pool, this is `internet` here the IP address is
`127.42.101.100`, for the next it is `127.42.101.101` and so on.

    user sniproxy
    pidfile /var/run/sniproxy.pid

    # vpn.example
    listen 192.0.2.1:443 {
        proto tls
        fallback 127.42.101.100:1194
        table https_hosts
    }

    # office-vpn.example
    listen 192.0.2.2:443 {
        proto tls
        fallback 127.42.101.101:1194
        table https_hosts
    }

    table https_hosts {
        vpn.example 127.42.101.100:8443
    }

Then, to restart sniproxy:

    $ sudo systemctl restart sniproxy

That should be all!
