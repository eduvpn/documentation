**WIP**

This does not work yet, and documentation is not complete, but this is the 
general direction. The "More Locations" actually has all the support now, but 
setting it up is a bit tricky still. Needs more documentation and be a lot 
easier.

# Multi Node

In a multi node configuration it becomes possible to use multiple servers as 
part of the same VPN service (instance). A node here is described as a server 
running the OpenVPN processes, it can be either a virtual or bare metal 
machine.

There are two scenarios where this can be useful:

- Increase scalability by distributing the load over multiple servers in the 
  same location;
- Allow for various PoPs around the world to allow users to choose the PoP 
  closest to their location to e.g. reduce the latency or avoid location based
  censorship.

**TODO** split this in two documents! One for each scenario!


## More Servers

In this scenario we create a "controller" node that runs the user portal, admin
portal and CA. It will share a (virtual) network with the other nodes that are
just running OpenVPN. This is configured by adding additional profiles to 
`/etc/vpn-server-api/vpn.example/config.yaml`.

**THIS IS CURRENTLY NOT WORKING!!**

    vpnProfiles:
        internet:
            profileNumber: 1
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
between the profiles. The `listen` address indicates the address used by the 
nodes, the `managementIp` is the address on the private virtual network 
between the instances. The `useProxy` option makes the OpenVPN instance 
listen on `TCP/443` directly as there won't be a SNI Proxy instance for 
sharing the traffic between a web server and OpenVPN on the VPN nodes.

The management node will have the `10.10.10.1` IP address so it can reach the
other nodes.

### TODO

- think more about whether `multiNode` will work like this?! Or do we need
  just need multiple profiles that have different IP addresses but somehow only
  show up once in the portal and admin?

## More Locations

The scenario here is the same as above, except we need to use something to 
establish a secure channel between the "controller" node and the OpenVPN nodes
and the various nodes **do** need to be listed for the user and administrator
as separate profiles.

You can use the `deploy_node.sh` script on a fresh CentOS install.

We can use e.g. [PeerVPN](https://peervpn.net/) for this. It can create a 
virtual network between all the nodes. 

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
        useProxy: false
        listen: 0.0.0.0
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
        useProxy: false
        listen: 0.0.0.0
        managementIp: 10.10.10.3

Make sure the DNS entries work!

### PeerVPN

**NOTE**: there is currently no RPM package for CentOS available, so I used 
the one for Fedora and rebuilt it on CentOS.

On a CentOS machine:

    $ sudo yum -y install fedora-packager gcc
    $ rpmdev-setuptree

Get the latest source RPM from here: 
http://koji.fedoraproject.org/koji/packageinfo?packageID=15018 and copy it in 
`$HOME/rpmbuild/SRPMS`.
    
    $ cd $HOME/rpmbuild/SRPMS
    $ rpmbuild --rebuild <peervpn-XXX.src.rpm>

At time of writing, this was `peervpn-0.044-1.fc25.src.rpm`.

    $ cd $HOME/rpmbuild/RPMS/x86_64
    $ sudo yum -y install <peervpn-XXX.rpm>

Make sure `udp/7000` is reachable on `vpn.example` from the other two nodes! 
Generate the `psk` like this:

    $ pwgen -s 32 -n 1

The configuration file on all machines is `/etc/peervpn/vpn.conf`.

On `vpn.example`:

    ifconfig4 10.42.42.1/24
    networkname VPN
    psk P2vH0aYuhVZZGZOITWvYer3p1qo57D2w

On `europe.vpn.example`:

    ifconfig4 10.42.42.2/24
    initpeers vpn.example 7000
    networkname VPN
    psk P2vH0aYuhVZZGZOITWvYer3p1qo57D2w

On `asia.vpn.example`:

    ifconfig4 10.42.42.3/24
    initpeers vpn.example 7000
    networkname VPN
    psk P2vH0aYuhVZZGZOITWvYer3p1qo57D2w

Now enable it on all the machines:

    $ sudo systemctl enable peervpn@vpn
    $ sudo systemctl start peervpn@vpn

All machines should be able to ping each other!

Generate the new server configurations:

**TODO** we didn't configure the node in 
`/etc/vpn-server-node/vpn.example/config.yaml` yet.
**TODO** talk about `firewall.yaml` to mark `tap+` as a trusted device.
**TODO** talk about OpenVPN not coming up on boot, because it is started before 
PeerVPN is ready.

On `europe.vpn.example`:

    $ sudo vpn-server-node-server-config --instance vpn.example --profile europe --generate --cn europe01.vpn.example

On `asia.vpn.example`:

    $ sudo vpn-server-node-server-config --instance vpn.example --profile asia --generate --cn asia01.vpn.example

