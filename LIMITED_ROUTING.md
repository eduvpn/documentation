# Introduction

Allow clients to authenticate to the VPN, but only have access to a restricted
set of resources.

# Scenarios

Alice manages the DNS servers that have management LAN with range
`10.0.4.0/24`, Eve manages the HTTP servers in the range `10.0.5.0/24`.

When Alice uses the VPN she should only be able to access the DNS server range 
and not the HTTP server range, and Eve should only be able to access the HTTP 
servers range.

# VPN Server

The VPN server has IP address `192.168.1.42`. It has the IP range `10.8.0.0/16`
to give to clients.

The VPN server has the ability to give a specific IP address to a particular
user. Alice has the CN `alice`, Eve has the CN `eve`.

To make this work, Alice gets an assigned IP address in the range `10.8.1.0/24`
and Eve gets an assigned IP address in the range `10.8.2.0/24`. This is 
accomplished by '--client-config-dir` directives below. If the CN is not 
found the connection should be terminated with a `disable` line in the 
`DEFAULT` file.

## Alice

    ifconfig-push 10.8.0.2 255.255.255.0

## Eve
    
    ifconfig-push 10.8.1.2 255.255.255.0

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
"HTTP servers". Selecting one would chose a free IP address in the range and 
assign that to the user automatically on next connect.
