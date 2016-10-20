# Distributed Nodes

This document describes how to configure multiple PoPs around the world to 
allow users to choose the PoP closest to their location to e.g. reduce the 
latency. This can all be done with one configuration. This document assumes
we have 3 VMs:

- Controller node running on `vpn.example` (installed using 
  `deploy_controller.sh`);
- VPN node on `europe.vpn.example` (installed using `deploy_node.sh`);
- VPN node on `asia.vpn.example` (installed using `deploy_node.sh`);

The controller node will run the various management components, and the VPN 
nodes will run OpenVPN.

The communication between the nodes and the controller will be done using 
[PeerVPN](https://peervpn.net/).

## Controller

On the controller node, `vpn.example`, we configure two profiles, that are 
running on different machines, in `/etc/vpn-server-api/vpn.example/config.yaml` 
configure the following:

    vpnProfiles:
        europe:
            profileNumber: 1
            displayName: 'Internet Access (Europe)'
            extIf: eth0
            useNat: true
            defaultGateway: true
            hostName: europe.vpn.example
            range: 10.0.0.0/24
            range6: 'fd00:4242:4242::/48'
            dns: [8.8.8.8, 8.8.4.4, '2001:4860:4860::8888', '2001:4860:4860::8844']
            dedicatedNode: true
            listen: '::'
            managementIp: 10.10.10.2

        asia:
            profileNumber: 2
            displayName: 'Internet Access (Asia)'
            extIf: eth0
            useNat: true
            defaultGateway: true
            hostName: asia.vpn.example
            range: 10.20.30.0/24
            range6: 'fd00:4445:4647::/48'
            dns: [8.8.8.8, 8.8.4.4, '2001:4860:4860::8888', '2001:4860:4860::8844']
            dedicatedNode: true
            listen: '::'
            managementIp: 10.10.10.3

**NOTE**: make sure the DNS entries, `europe.vpn.example` and 
`asia.vpn.example` point to the OpenVPN nodes for IPv4 (and optionally IPv6).

### Firewall

**TODO**: `deploy_controller` should set this up properly, it is static anyway.

### PeerVPN

Generate the `psk` using `pwgen -s 32 -n 1`.

`/etc/peervpn/vpn.conf`:

    networkname VPN
    psk P2vH0aYuhVZZGZOITWvYer3p1qo57D2w
    interface tap0

`/etc/sysconfig/network-scripts/ifcfg-tap0`:

    DEVICE="tap0"
    ONBOOT="yes"
    TYPE="Tap"
    IPADDR=10.42.42.1
    PREFIX=24

Enable and activate PeerVPN:

    $ sudo ifup tap0
    $ sudo systemctl enable peervpn@vpn
    $ sudo systemctl start peervpn@vpn

## Nodes

### PeerVPN

`/etc/peervpn/vpn.conf`:

    initpeers vpn.example 7000
    networkname VPN
    psk P2vH0aYuhVZZGZOITWvYer3p1qo57D2w
    interface tap0

To configure the `tap` interfaces on the nodes, give each of them the matching
`managementIp` from the controller configuration above.

`/etc/sysconfig/network-scripts/ifcfg-tap0` (replace the `IPADDR` with the
IP address from `managementIp`):

    DEVICE="tap0"
    ONBOOT="yes"
    TYPE="Tap"
    IPADDR=10.42.42.X
    PREFIX=24

Enable and activate PeerVPN:

    $ sudo ifup tap0
    $ sudo systemctl enable peervpn@vpn
    $ sudo systemctl start peervpn@vpn

Make sure you can reach the controller:

    $ ping 10.42.42.1

### Firewall Configuration

Update `/etc/vpn-server-node/firewall.yaml` to enable `tap0` under 
`trustedInterfaces`.

### VPN Configuration

Update `/etc/vpn-server-node/vpn.example/config.yaml` to point the `apiUri` to 
`10.42.42.1`  and copy/paste the `userPass` from the controller node 
configuration from `/etc/vpn-ca-api/vpn.example/config.yaml` and 
`/etc/vpn-server-api/vpn.example/config.yaml` to allow this node to talk to 
the APIs.

Now it should be possible to generate the configuration on the nodes, the 
example is for `europe.vpn.example`, but it is similar for `asia.vpn.example`:

    $ sudo vpn-server-node-server-config --instance vpn.example --profile europe --generate --cn europe01.vpn.example
    $ sudo vpn-server-node-generate-firewall --install

Enable and start:

    $ sudo systemctl enable openvpn@server-vpn.example-europe-{0,1,2,3}
    $ sudo systemctl start openvpn@server-vpn.example-europe-{0,1,2,3}

Restart the firewall:

    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables

