# Client Implementation Notes

In order to understand how to best create an implementation of an eduVPN and 
Let's Connect! client, we collected some notes that will hopefully help you 
create a better client.

This builds on the following documents:

* [API](API.md)
* [Server Discovery](SERVER_DISCOVERY.md) (eduVPN-only)

## Fail-over

The VPN client SHOULD implement support for both OpenVPN and WireGuard. OpenVPN
allows for both UDP and TCP. WireGuard only supports UDP.

Some networks block or mangle UDP connections and thus TCP is required. In the 
field we saw the following issues with UDP:

1. UDP connections are completely blocked on the network level;
2. UDP connections do not handle UDP packets of the MTU size properly.

In scenario (1) OpenVPN itself has a mechanism to fall back to TCP. It will 
try to connect using UDP, figures out that it doesn't work after a timeout and
retry with TCP. WireGuard will silently fail in this scenario.

With scenario (2) OpenVPN will also silently fail. The OpenVPN connection 
appears to be up, but it does not actually work when traffic reaches the MTU of
the connection and it will be silently dropped. A simple _ping_ over the 
connection *does* work as those packets do not get close to reaching the MTU 
size. WireGuard will also fail in this scenario as _all_ packets sent/received
by WireGuard have the exact same size.

**TODO**: is this statement about WireGuard actually true? Citation needed.

In order to resolve this situation, the client can implement a connection 
check:

1. Send a ping packet over the VPN of maximum MTU that is supposed to work;
2. Wait for the ping response to arrive.

If the ping response arrives, we know the VPN connection works!

The VPN can determine the _gateway_ in order to determine where to send a 
ping to. The gateway can be determined by calculating the first host in the
network based on the IP assigned to the VPN client. As an example, if the VPN 
client gets the IP address `10.10.10.5/24`, the IP address of the gateway is
`10.10.10.1`. If the VPN client gets the IP address `fd42::5/112` the IP 
address of the gateway is `fd42::1`.

**NOTE** you MUST implement proper gateway calculation and not simply set the 
last _octet_ to `.1` for IPv4 addresses. For example, the gateway of the 
IP address `10.10.10.130/25` is not `10.10.10.1`, but `10.10.10.129`. For IPv6
using `::1` coincidentally _does_ work in the case of eduVPN / Let's Connect! 
servers.

**NOTE** we do not implement real "online detection" as not all VPNs are used
to access the Internet, some only are used to reach resources at the 
organization and send other traffic _outside_ the VPN, i.e. "split tunnel".

The client takes the following steps:

1. Establish connection using WireGuard or OpenVPN over UDP;
2. Send a ping to the gateway;
3. Wait for the ping response (e.g. maximum 10 seconds);
4. If ping does NOT return:
    * Verify the VPN server supports OpenVPN over TCP
    * Attempt to connect over TCP

If a VPN profile does not support OpenVPN over TCP, the client can give a 
notice that the VPN connection is not working and leave it at that.

**NOTE**: the client MUST take care that the "online detection" does NOT 
interfere with OpenVPN's own fail-over mechanism, i.e. if multiple `remote` 
entries are specified of which one is TCP.
