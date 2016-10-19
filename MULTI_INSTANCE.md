**WIP**

# Multi Instance

The software supports deploying various instances on one machine. This means
that one installation can host multiple VPN installations on multiple domains,
e.g. it can support both `https://vpn.foo.org/` and `https://vpn.bar.org`.

These instances are completely separated, they have their own configuration 
folders, their own CA, their own data store and run their own OpenVPN 
processes. Every instance can again have their own pools again, see 
[Multi Pools](MULTI_POOLS.md).

In the below example we will add the `vpn.bar.org` instance to the existing
`vpn.example` instance.

**TODO**: create a deploy-like script to add an instance.
**TODO**: use the script to sync the secrets
**TODO**: (optionally) use the IP address generator script
**TODO**: write script to set the instanceNumber and the IP addresses
**TODO**: write script to generate sniproxy.conf based on the configs
**TODO**: write script to generate httpd.conf based on the configs
**TODO**: add `listen6` directive to config for use by sniproxy and socat for 
fixing IPv6

# CA API

    $ sudo mkdir /etc/vpn-ca-api/vpn.bar.org
    $ sudo cp /usr/share/doc/vpn-ca-api-*/config.yaml.example /etc/vpn-ca-api/vpn.bar.org/config.yaml

The file `/etc/vpn-ca-api/vpn.bar.org/config.yaml` can be modified if needed. 
Now to initialize the CA for this instance:

    $ sudo -u apache vpn-ca-api-init --instance vpn.bar.org

That's it for the CA.

# Server API

    $ sudo mkdir /etc/vpn-server-api/vpn.bar.org
    $ sudo cp /usr/share/doc/vpn-server-api-*/config.yaml.example /etc/vpn-server-api/vpn.bar.org/config.yaml

Now this configuration file MUST be modified. 

    instanceNumber: 1

This line MUST be changed, into something unique. Every `instanceNumber` can 
only occur once, here we choose:

    instanceNumber: 5

The `vpnPools` section can be updated, see 
[Pool Configuration](POOL_CONFIG.md) for more information.

    $ sudo -u apache vpn-server-api-init --instance vpn.bar.org

# Server Node

    $ sudo mkdir /etc/vpn-server-node/vpn.bar.org
    $ sudo cp /usr/share/doc/vpn-server-node-*/config.yaml.example /etc/vpn-server-node/vpn.bar.org/config.yaml

Here in this configuration file you also need to modify the `apiUrl` to point 
to the correct IP address. The IP address will be `127.42.10x.100`, where `x` 
is the `instanceNumber`, so in this example it will be `127.42.105.100` 
because `instanceNumber` is `5`.

# User Portal

    $ sudo mkdir /etc/vpn-user-portal/vpn.bar.org
    $ sudo cp /usr/share/doc/vpn-user-portal-*/config.yaml.example /etc/vpn-user-portal/vpn.bar.org/config.yaml

Here in this configuration file you also need to modify the `apiUrl` to point 
to the correct IP address, `127.42.105.100`.

To add a user:

    $ sudo vpn-user-portal-add-user --instance vpn.bar.org --user foo --pass bar

# Admin Portal

    $ sudo mkdir /etc/vpn-admin-portal/vpn.bar.org
    $ sudo cp /usr/share/doc/vpn-admin-portal-*/config.yaml.example /etc/vpn-admin-portal/vpn.bar.org/config.yaml

Here in this configuration file you also need to modify the `apiUrl` to point 
to the correct IP address, `127.42.105.100`.

To add a user:

    $ sudo vpn-admin-portal-add-user --instance vpn.bar.org --user foo --pass bar

# Apache

For the new instance you can copy the 
[Apache template](https://raw.githubusercontent.com/eduvpn/documentation/master/resources/vpn.example.conf) 
to  `/etc/httpd/conf.d/vpn.bar.org.conf`. Replace all occurrences of 
`vpn.example` in that file with `vpn.bar.org`. Also update the IP addresses
used there, i.e. replace `127.42.101.100` with `127.42.105.100`.

You then install a new certificate for `vpn.bar.org` as well, see the template
for where to store the certificate and chain.

    $ sudo systemctl restart httpd

# Server Node (2)

Now that this works, it should be possible to generate the server configuration
for your new instance.

    $ sudo vpn-server-node-server-config --instance vpn.bar.org --pool internet --generate --cn vpn01.bar.org
    $ sudo systemctl enable openvpn@server-vpn.bar.org-internet-{0,1,2,3}
    $ sudo systemctl start openvpn@server-vpn.bar.org-internet-{0,1,2,3}

And the firewall:

    $ sudo vpn-server-node-generate-firewall --install
    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables

# sniproxy

TBD.
