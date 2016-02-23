# Introduction

We want to create a setup where certain users of the VPN will be placed in a 
special IP range that has additional permissions, e.g. accessing internal 
services to perform management in addition to browsing the web.

# Use Case

All users part of an organization can connect to a VPN server, but Bob and Eve 
are working for accounting and have access to the accounting server over the 
VPN. The other users do not have that privilege and can only use the VPN to 
browse the web.

We assume here that the security of the accounting service is not sufficient
to rely on its built in authentication system. We want to make sure that users
other than Bob and Eve cannot even connect to that server.

The account server lives in its own VLAN and the switch has the ability to 
implement IP filtering. The VLAN has the IP range `10.10.10.0/29`.

# Solution

The VPN server will classify the users in two categories. Accounting employees
and the rest. Currently only Bob and Eve need access to the accounting server,
but in the future there could be more people who need access.

The VPN server has `10.5.5.0/24` to use for clients. We will reserve a small 
part of this range for people who need to access the accounting VLAN. The 
switch will then use this range to filter access.

We will reserve 10.5.5.248 up to 10.5.5.254 for accounting, so 6 possible 
clients. 

# VPN Server

Instead of using:

    server 10.5.5.0 255.255.255.0
#    ifconfig-pool 10.5.5.2 10.5.5.247 255.255.255.0

We will be using its expanded form slightly modified:

**TEST IF WE CAN JUST OVERRIDE THE --server WITH CUSTOM IFCONFIG**
  
    mode server
    tls-server
    push "topology subnet"
    ifconfig 10.5.5.1 255.255.255.0
    ifconfig-pool 10.5.5.2 10.5.5.247 255.255.255.0
    push "route-gateway 10.5.5.1"

<!--if route-gateway unset:-->
<!--       route-gateway 10.8.0.2-->


The VPN server has IP address `192.168.1.42`. It has the IP range `10.8.0.0/16`
to give to clients.

The VPN server has the ability to give a specific IP address to a particular
user. Alice has the CN `alice`, Eve has the CN `eve`.

To make this work, Alice gets an assigned IP address in the range `10.8.1.0/24`
and Eve gets an assigned IP address in the range `10.8.2.0/24`. This is 
accomplished by '--client-config-dir` directives below.



    server 10.8.0.0 255.255.0.0 nopool
    ccd-exclusive

All other pushes can be removed from the server configuration.

## Alice

    ifconfig-push 10.8.1.2 255.255.255.0
    push "route 10.0.4.0 255.255.255.0"

## Eve
    
    ifconfig-push 10.8.2.2 255.255.255.0
    push "route 10.0.5.0 255.255.255.0"

# Firewall

Where `eth0` is the outgoing interface.

    -A FORWARD -p icmp -j ACCEPT
    -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

    # DNS servers
    -A FORWARD -i tun+ -o eth0 -s 10.8.1.0/24 -d 10.0.4.0/24 -j ACCEPT
    # HTTP servers
    -A FORWARD -i tun+ -o eth0 -s 10.8.2.0/24 -d 10.0.5.0/24 -j ACCEPT

    -A FORWARD -j REJECT --reject-with icmp-host-prohibited

# Management Interface

It must be possible to configure an IP/range for a particular user in the 
management UI. Ideally only a "role" needs to be specified where the rest is 
automated. In this case there would be two roles: "DNS servers" and 
"HTTP servers". Selecting one would choose a free IP address in the range and 
assign that to the user automatically on next connect.
