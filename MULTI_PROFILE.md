**WIP**

# Multi Profile

Every VPN [instance](MULTI_INSTANCE.md) supports multiple "profiles". This 
means that every instance can host multiple "deployment scenarios". For 
instance there can be two profiles, one for employees, `office`, and one for 
network administrators, `admin`. They can have completely different 
configurations, ACLs based on group membership and optionally two-factor 
authentication.

Below a configuration example is given for exactly this scenario. An 
organization has employees and administrators. The employees can access the VPN
to access the organization's resources, while the administrators can access 
additional networks to manage servers. The administrators are determined by the
ACL and have two-factor authentication enabled as to provide extra security.

We assume the instance is running as `https://vpn.example/` and was initially
deployed using the provided deploy script.

The configuration is done in `/etc/vpn-server-api/vpn.example/config.yaml`.

## Configuration

First we configure the `office` profile. Clients will get an IP address in the 
range `10.0.5.0/24`. The clients will have access to the organization's 
networks `192.168.0.0/24` and `192.168.1.0/24`. The administrators will get
an IP address in the range `10.0.10.0/24` and have access to the additional
network `192.168.5.0/24`.

    vpnProfiles:
        internet:
            profileNumber: 1
            displayName: 'Office'
            extIf: eth0
            listen: 192.0.2.1
            hostName: office.vpn.example
            range: 10.0.5.0/24
            range6: 'fd10:0:5::/48'
            routes: ['192.168.0.0/24', '192.168.1.0/24']

        admin:
            profileNumber: 2
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

    groupProviders:
        StaticProvider:
            admin:
                displayName: Administrators
                members: [john, jane]

[More](PROFILE_CONFIG.md) configuration options are available.

# Deploy

In order to activate, new configuration files for the OpenVPN processes need
to be generated, the processes restarted and some other configuration changes
need to be made.

## Disable Old Configuration

If you are currently running the default `vpn.example` with the `internet` 
profile you can disable and stop them like this:

    $ sudo systemctl stop    openvpn-server@vpn.example-internet-{0,1,2,3}
    $ sudo systemctl disable openvpn-server@vpn.example-internet-{0,1,2,3}
 
Remove the old configuration files, and the certificates/keys:

    $ sudo rm /etc/openvpn/server-vpn.example-internet-{0,1,2,3}.conf
    $ sudo rm -rf /etc/openvpn/tls/vpn.example/internet

## Generate New Configuration
 
To generate the new configuration files and certificates/keys for the newly 
created profiles, run these commands:

    $ sudo vpn-server-node-server-config --instance vpn.example --profile office \
        --generate --cn office01.vpn.example
    $ sudo vpn-server-node-server-config --instance vpn.example --profile admin \
        --generate --cn admin01.vpn.example

Enable them on boot and start them:

    $ sudo systemctl enable openvpn-server@vpn.example-office-{0,1,2,3}
    $ sudo systemctl enable openvpn-server@vpn.example-admin-{0,1,2,3}
    $ sudo systemctl start  openvpn-server@vpn.example-office-{0,1,2,3}
    $ sudo systemctl start  openvpn-server@vpn.example-admin-{0,1,2,3}

Regenerate and restart the firewall:

    $ sudo vpn-server-node-generate-firewall --install
    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables

## SNI Proxy

It is no longer possible for sniproxy to listen on `0.0.0.0` as it is 
impossible to detect which OpenVPN connection over `tcp/443` belongs to which
profile, so sniproxy must also bind to the IP addresses as defined above. The 
default configuration, as shows below needs to be modified:

    user sniproxy
    pidfile /var/run/sniproxy.pid

    listen 80 {
        proto http
        table http_hosts
    }

    listen 443 {
        proto tls
        fallback 127.42.101.100:1194
        table https_hosts
    }

    table http_hosts {
        vpn.example 127.42.101.100:8080
    }

    table https_hosts {
        vpn.example 127.42.101.100:8443
    }

The modification will look like this. Note the `listen` line where the IP 
address now matches the `listen` directive from the above profile config. In 
the line with `fallback` the IP address used is the one on which the OpenVPN 
process listens. For the first profile, this is `internet` here the IP address 
is `127.42.101.100`, for the next it is `127.42.101.101` and so on.

**TODO**: it does not really make sense that the web server will listen on both
IP addresses, we should have different host names for the OpenVPN endpoints, 
e.g. `internet.vpn.example` and `office.vpn.example`, then this is not needed
like this! We could even get rid of sniproxy if we have separate IP addresses
for the web interface and the OpenVPN processes. We should use sniproxy only
for 'single IP deploys'

    user sniproxy
    pidfile /var/run/sniproxy.pid

    # office.vpn.example
    listen 192.0.2.1:80 {
        proto http
        table http_hosts
    }

    listen 192.0.2.1:443 {
        proto tls
        fallback 127.42.101.100:1194
        table https_hosts
    }

    # admin.vpn.example
    listen 192.0.2.2:80 {
        proto http
        table http_hosts
    }

    listen 192.0.2.2:443 {
        proto tls
        fallback 127.42.101.101:1194
        table https_hosts
    }

    table http_hosts {
        vpn.example 127.42.101.100:8080
    }

    table https_hosts {
        vpn.example 127.42.101.100:8443
    }

Then, to restart sniproxy:

    $ sudo systemctl restart sniproxy

That should be all!
