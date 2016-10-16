**WIP**

This does not work yet, and documentation is not complete, but this is the 
general direction. The "More Locations" actually has all the support now in 
vpn-server-api, but setting it up is a bit tricky still. Needs more 
documentation.

# Multi Node

In a multi node configuration it becomes possible to use multiple servers as 
part of the same VPN service (instance). A node here is described as a server 
running the OpenVPN processes, it can be either a virtual or bare metal 
machine.

There are two scenarios where this can be useful:

- Increase scalability by distributing the load over multiple servers in the 
  same location;
- Allow for various PoPs around the world to allow users to choose the PoP 
  closest to their location to reduce the latency.

## More Servers

In this scenario we create a "controller" node that runs the user portal, admin
portal and CA. It will share a (virtual) network with the other nodes that are
just running OpenVPN. This is configured by adding additional pools to 
`/etc/vpn-server-api/vpn.example/config.yaml`.

    vpnPools:
        internet:
            poolNumber: 1
            displayName: 'Internet Access'
            extIf: eth0
            useNat: true
            defaultGateway: true
            hostName: vpn.example
            dns: [8.8.8.8, 8.8.4.4, '2001:4860:4860::8888', '2001:4860:4860::8844']

            multiNode:
                one: 
                    range: 10.0.0.0/24
                    range6: 'fd00:4242:4242::/48'
                    managementIp: 10.10.10.2
                    useProxy: false
                    listen: 192.0.2.55
                two:
                    range: 10.0.1.0/24
                    range6: 'fd00:4242:4243::/48'
                    managementIp: 10.10.10.3
                    useProxy: false
                    listen: 192.0.2.66

Notice the changing `listen` and `managementIp`, `range` and `range6` values 
between the pools. The `listen` address indicates the address used by the 
nodes, the `managementIp` is the address on the private virtual network 
between the instances. The `useProxy` option makes the OpenVPN instance 
listen on `TCP/443` directly as there won't be a SNI Proxy instance for 
sharing the traffic between a web server and OpenVPN on the VPN nodes.

The management node will have the `10.10.10.1` IP address so it can reach the
other nodes.

### TODO

- think more about whether `multiNode` will work like this?! Or do we need
  just need multiple pools that have different IP addresses but somehow only
  show up once in the portal and admin?

## More Locations

The scenario here is the same as above, except we need to use something to 
establish a secure channel between the "controller" node and the OpenVPN nodes
and the various nodes **do** need to be listed for the user and administrator
as separate pools. 

We use [PeerVPN](https://peervpn.net/) for this. It can create a virtual 
network between all the nodes. 

vpnPools:
    europe:
        poolNumber: 1
        displayName: 'Internet Access (Europe)'
        extIf: eth0
        useNat: true
        defaultGateway: true
        hostName: europe.vpn.example
        range: 10.0.0.0/24
        range6: 'fd00:4242:4242::/48'
        dns: [8.8.8.8, 8.8.4.4, '2001:4860:4860::8888', '2001:4860:4860::8844']
        useProxy: false
        listen: 192.0.2.33
        managementIp: 10.10.10.2

    asia:
        poolNumber: 2
        displayName: 'Internet Access (Asia)'
        extIf: eth0
        useNat: true
        defaultGateway: true
        hostName: asia.vpn.example
        range: 10.20.30.0/24
        range6: 'fd00:4445:4647::/48'
        dns: [8.8.8.8, 8.8.4.4, '2001:4860:4860::8888', '2001:4860:4860::8844']
        useProxy: false
        listen: 192.0.2.44
        managementIp: 10.10.10.3

Make sure the DNS entries work as well.

### PeerVPN

TBD.
