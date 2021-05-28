---
title: Guest Usage
description: Setup and Enable Guest Usage (VPN Federation)
category: advanced
---

The VPN server software implements "Guest Usage". This means that users of one
VPN server deployment, e.g operated by organization A, can use another 
deployment, say operated by organization B, and vice versa.

The trust created between the VPN servers is based on signatures over OAuth 2.0
access tokens. Each server can configure public keys of other VPN servers it
trusts, thus allowing users of those lists servers to access its VPN service
as well.

This "Guest Usage" scenario is OPTIONAL and **DISABLED** by default.

# Configuration

In the file `/etc/vpn-user-portal/config.php` you need to enable 
`remoteAccess`:

```
// ...

'Api' => [
    'remoteAccess' => true,
],

// ...
```

# Registration

If you want to register your server for eduVPN, please contact 
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org) and 
provide the following information:

The following information needs to be provided in order to be added:

* A *generic* contact email address to be contacted for general inquiries, to 
  be listed on the [Contact](contact.html#server-operators) page;
* An *abuse* contact email address to be contacted in case of abuse (preferably 
  a role-based mail address);
* A *technical* contact email address to be contacted in case of technical 
  problems (preferably a role-based mail address);
* End-user support contact(s), at least one of: mail, URL, phone number.
  **NOTE** these will become public;
* A web site we can refer end-users to for this particular _Secure Internet_ 
  server (Optional);
* The full hostname (FQDN) of your VPN server;
* Make sure TLS is configured properly! Use e.g. 
  [SSL Server Test](https://www.ssllabs.com/ssltest/);
* The name of the country / region your VPN server is located in (English);
* Full information on any filtering/blocking of traffic by your VPN server or 
  upstream network(s), either because of legal reasons or local policy;
* The public key of your server (`sudo vpn-user-portal-show-oauth-key`), make
  sure to enable 
  [guest access](https://github.com/eduvpn/documentation/blob/v2/GUEST_USAGE.md)!;
* A signed copy of the 
  [policy](download/eduVPN_Compliance_Statement_1.0.pdf) document by a 
  person authorized to do so at your organization;
* Send your request to 
  [eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org), use
  "_Add [${FQDN}] to Secure Internet eduVPN_" as title.
  
#### Template

Use the following example template in your mail to 
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org), please
update all values for your situation:

Subject: `Add [vpn.example.org] to Secure Internet eduVPN`

Body:
```
Generic Contact: admin@example.org
Abuse Contact: abuse@example.org
Technical Contact: eduvpn@example.org
End-user Support Contact: 
  - support@example.org
  - +1234567890
  - https://support.example.org/
Information Website: https://www.example.org/services/eduvpn
FQDN: vpn.example.org
Country / Region: The Netherlands
Restrictions: 
  - in/outbound tcp/25 blocked
Public Key: O53DTgB956magGaWpVCKtdKIMYqywS3FMAC5fHXdFNg
```

Do **NOT** forget to attach the signed copy of the policy document!
