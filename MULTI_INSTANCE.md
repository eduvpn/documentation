# Multi Instance

The software supports deploying various instances without requiring a new host
for a new instance. This means that one installation can host multiple VPN 
installations on multiple domains, e.g. it can support both 
`https://vpn.foo.org/` and `https://vpn.bar.org`.

These instances are separated, they have their own configuration 
folders, their own CA, their own data store and run their own OpenVPN 
processes. Every instance can again have their own profiles again, see 
[Multi Profile](MULTI_PROFILE.md).

Technically it _is_ possible to run everything on one host, but that will 
quickly become complicated, regarding SNI Proxy and port sharing. This is *NOT* 
supported.

We recommend using (at least) two machines, one controller (running the
portals, API and CA) and a "node" running the OpenVPN processes.

# Network

We assume you have two nodes, connected using a "private" network that is not 
reachable over the Internet. You can configure a "private VLAN" in the VM 
platform that exposes an extra NIC in the VMs or use something like 
[tinc](https://www.tinc-vpn.org/) to create a virtual private network.

# Controller

On the controller machine you install `vpn-user-portal`, `vpn-admin-portal` 
and `vpn-server-api`. 

You configure the IP addresses of the instances on this interface. Every 
instance will have a unique number configured in 
`/etc/vpn-server-api/<FQDN>/config.php` called `instanceNumber`, if you 
have three instances, e.g. `1`, `2` and `3` you bind the IP addresses 
`10.42.101.100`, `10.42.102.100` and `10.42.103.100` to the private network 
interface. Make sure each instance has `managementIp` set to `auto` and 
`portShare` to `false`.

Every instance gets their own HTTP configuration file in 
`/etc/httpd/conf.d/<FQDN>.conf` that reflects these IP addresses as well. See
`resources/controller/vpn.example.conf` for a template.

The `deploy_controller.sh` script sets up one instance and sets up tinc to 
communicate with the node(s). This script can be used to set up the first 
instance, and add more instances later manually.

Every instance needs to be "initialized" to create the CA and related DB:

    $ sudo vpn-server-api-init --instance <FQDN>

# Node

On the node machine you install `vpn-server-node`.
