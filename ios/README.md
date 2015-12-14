# iOS
There are number of things you have to consider when using OpenVPN on iOS, 
please refer to the OpenVPN 
[iOS FAQ](https://docs.openvpn.net/docs/openvpn-connect/openvpn-connect-ios-faq.html).
 
Interesting quotes from this FAQ:

> Many Apple services such as Push Notifications and FaceTime are never routed through the VPN tunnel, as per Apple policy.

# Configuration

There are two issues with using OpenVPN on iOS with eduVPN:

1. IPv4 traffic is by default not routed over the VPN on iOS >= 9. This is 
   due to a bug in iOS/OpenVPN when IPv6 is enabled. eduVPN has IPv6 
   enabled, it is 2015...;
2. The default cipher suite selected is insecure and has to be modified to
   work with eduVPN.

To fix the first issue, you have to enable `Seamless tunnel` under 
`Connection Settings`

To fix the second issue, you have to **disabled** `Force AES-CBC ciphersuites` 
under `Advanced Settings`.
