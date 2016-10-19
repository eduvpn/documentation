**WIP**

# Multi Pool

Every VPN [instance](MULTI_INSTANCE.md) supports multiple "pools". This means 
that every instance can host multiple "deployment scenarios". For instance 
there can be two pools, one for employees, `office`, and one for network 
administrators, `admin`. They can have completely different configurations, 
ACLs based on group membership and optionally two-factor authentication.

Below a configuration example is given for exactly this scenario. An 
organization has employees and administrators. The employees can access the VPN
to access the organization's resources, while the administrators can access 
additional networks to manage servers. The administrators are determined by the
ACL and have two-factor authentication enabled as to provide extra security.

We assume the instance is running as `https://vpn.example/` and was deployed 
using the provided deploy script.

The configuration is done in `/etc/vpn-server-api/vpn.example/config.yaml`.

## Configuration

First we configure the `office` pool. Clients will get an IP address in the 
range `10.0.5.0/24`. The clients will have access to the organization's 
networks `192.168.0.0/24` and `192.168.1.0/24`. The administrators will get
an IP address in the range `10.0.10.0/24` and have access to the additional
network `192.168.5.0/24`.

    vpnPools:
        internet:
            poolNumber: 1
            displayName: 'Office'
            extIf: eth0
            listen: 192.0.2.1
            hostName: office.vpn.example
            range: 10.0.5.0/24
            range6: 'fd10:0:5::/48'
            routes: ['192.168.0.0/24', '192.168.1.0/24']

        admin:
            poolNumber: 2
            displayName: 'Administrators'
            extIf: eth0
            listen: 192.0.2.2
            hostName: admin.vpn.example
            range: 10.0.10.0/24
            range6: 'fd10:0:10::/48'
            routes: ['192.168.0.0/24', '192.168.1.0/24', '192.168.5.0/24']
            twoFactor: true
            enableAcl: true
            aclGroupList: [admin]
            aclGroupProvider: StaticGroups

    groupProviders:
        StaticProvider:
            admin:
                displayName: Administrators
                members: [john, jane]

[More](POOL_CONFIG.md) configuration options are available.

# Deploy

In order to activate, new configuration files for the OpenVPN processes need
to be generated, the processes restarted and some other configuration changes
need to be made.

**TODO**: we need to remove any old configurations and stop old VPN processes

To generate the new configuration files and certificates for the newly 
created pools, run these commands:

    $ sudo vpn-server-node-server-config --instance vpn.example --pool office \
        --generate --cn office01.vpn.example
    $ sudo vpn-server-node-server-config --instance vpn.example --pool admin \
        --generate --cn admin01.vpn.example
    $ sudo vpn-server-node-generate-firewall --install

Restart the firewall:

    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables


$ su -c 'for F in `ls /etc/systemd/system/multi-user.target.wants/*openvpn*`; do B=`basename $F` ; systemctl disable $B ; done;'

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

    # office.vpn.example
    listen 192.0.2.1:443 {
        proto tls
        fallback 127.42.101.100:1194
        table https_hosts
    }

    # admin.vpn.example
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
