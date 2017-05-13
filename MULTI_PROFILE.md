# Multi Profile

It is possible to add additional "profiles" to a VPN service. This is useful 
when you for example have two categories of users using the same VPN server,
e.g. "employees" and "administrators". 

**NOTE**: it is *NOT* recommended to use a single machine/VM for this, as this
will require using SNI Proxy, see below.

**NOTE**: every profile needs their own dedicated IPv4 or IPv6 address. 
OpenVPN can not listen on both an IPv4 address and and IPv6 address, unless it
is the special address `::`, which is only possible if there is only one 
profile. This becomes so complicated because we want to make `tcp/443` 
available for _every_ profile for clients to connect to.

See this [issue](https://github.com/eduvpn/vpn-server-node/issues/8) for a 
possible solution for needing the complicated "listen" solution.

# Configuration

The configuration takes place in `/etc/vpn-server-api/vpn.example/config.php`, 
assuming you are using `vpn.example`. Here we define two profiles, `office` and
`admin`:

    'vpnProfiles' => [

        // Office Employees
        'office' => [
            'profileNumber' => 1,
            'displayName' => 'Office',
            ...
            ...
            'extIf' => 'eth0',
            'listen' => '192.0.2.1',
            'hostName' => 'office.vpn.example',
            range: 10.0.5.0/24
            range6: 'fd10:0:5::/48'
            routes: ['192.168.0.0/24', '192.168.1.0/24']
        ],

        // Administrators
        'admin' => [
            'profileNumber' => 2,
            'displayName' => 'Administrators',
            ...
            ...
            'extIf' => 'eth0',
            'listen' => '192.0.2.2',
            'hostName' => 'admin.vpn.example',
            range: 10.0.10.0/24
            range6: 'fd10:0:10::/48'
            routes: ['192.168.0.0/24', '192.168.1.0/24', '192.168.5.0/24']
        ],
    ],

In this scenario, `extIf` is actually the interface where the traffic needs 
to go, so the "LAN" interface of the VPN server. The IP address mentioned in
`listen` MUST be bound to the DNS name specified in `hostName`.

# Additional Configuration

It is e.g. possible to activate [Two-factor Authentication](2FA.md) for the 
`admin` profile, or see [Profile Configuration](PROFILE_CONFIG.md) for more
configuration options.

# Activate

If you had an old profile, e.g. the default `internet`, it needs to be stopped
first, and can be removed:

    $ sudo systemctl stop    openvpn-server@vpn.example-internet-{0,1,2,3}
    $ sudo systemctl disable openvpn-server@vpn.example-internet-{0,1,2,3}
    $ sudo rm /etc/openvpn/server/vpn.example-internet-{0,1,2,3}.conf
    $ sudo rm -rf /etc/openvpn/server/tls/vpn.example/internet

Now the new configurations can be generated:

    $ sudo vpn-server-node-server-config --instance vpn.example --profile office --generate 
    $ sudo vpn-server-node-server-config --instance vpn.example --profile admin --generate

Enable and start them:

    $ sudo systemctl enable openvpn-server@vpn.example-office-{0,1,2,3}
    $ sudo systemctl enable openvpn-server@vpn.example-admin-{0,1,2,3}
    $ sudo systemctl start  openvpn-server@vpn.example-office-{0,1,2,3}
    $ sudo systemctl start  openvpn-server@vpn.example-admin-{0,1,2,3}

Regenerate and restart the firewall:

    $ sudo vpn-server-node-generate-firewall --install
    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables
