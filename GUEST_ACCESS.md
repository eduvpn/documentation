# Introduction

This document describes how to enable "Guest Access". This is a feature 
provided to the eduVPN community. It is NOT available for Let's Connect!.

Participating NRENs configure an eduVPN server to allow users from 
servers hosted by other NRENs to access their VPN server as well. 

This means for example that a user from the eduVPN server hosted in The
Netherlands by SURF can access the VPN server in Germany hosted by DFN.

**NOTE**: the "Guest Access" server MUST be a server dedicated ONLY for 
this purpose. It MUST NOT be used for any other purpose like providing 
access to restricted resources on the network!

# Eligibility / Requirements

Only NRENs are able to register a server for "Guest Access". 

You MUST use SAML authentication for your VPN server and provide us 
with a link to the SAML metadata for all IdPs (Identity Providers) that
have access to your server. We need this information to populate the 
organizations list in the eduVPN applications. Without SAML
metadata URL you can still participate, but your local users won't be
able to access any of the other "Guest Access" servers.

Currently we do NOT recommend registering your VPN server in eduGAIN!

In order to enable "Guest Access" on your server you MUST have 
`vpn-user-portal` >= 3.1. In older versions it will NOT work.

# Configuration

The "Guest Access" functionality MUST be manually enabled.

You need to edit `/etc/vnp-user-portal/config.php` and modify the `Api` 
section:

```php
'Api' => [
	'enableGuestAccess' => true,
]
```

Next you need to generate a HMAC key that will be used to "obfuscate" the user 
identifiers of your users as to not "leak" them to other NREN servers.

```bash
$ sudo /usr/libexec/vpn-user-portal/generate-secrets --hmac
```

# Public Key

We need to register your OAuth public key in our "discovery" file 
to allow all participating servers to fetch it and allow users from
your VPN service.

You can find this Public Key by going to the "Info" tab in your VPN 
portal. Expand the "Server" section by clicking "More" and look for 
"Public Key" under "OAuth". It has the following form:

```
k7.pub.ozEaVoU0p1HezQ41.HmV1WLVuRDoPiYoa2pP0qxP1YpWdKr5AoMdV_ZWl4i4
```

Make note of this public key as you need it for your server's registration.

# Registration

Please contact 
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org) and 
provide use with the following information:

* A *generic* contact email address to be contacted for general inquiries, to 
  be listed on the [Participants](https://www.eduvpn.org/countries/) page;
* An *abuse* contact email address to be contacted in case of abuse (preferably 
  a role-based mail address);
* A *technical* contact email address to be contacted in case of technical 
  problems (preferably a role-based mail address);
* End-user support contact(s), at least one of: mail, URL, phone number.
  **NOTE** these will become public;
* A web site we can refer end-users to for this particular _Secure Internet_ 
  server (Optional);
* The SAML metadata URL that contains all the organizations that have access 
  to your server which will be used to populate the eduVPN applications, i.e. 
  the **IdP** (federation) metadata URL;
* The full hostname (FQDN) of your VPN server;
* Make sure TLS is configured properly! Use e.g. 
  [SSL Server Test](https://www.ssllabs.com/ssltest/);
* The name of the country / region your VPN server is located in (English);
* Full information on any filtering/blocking of traffic by your VPN server or 
  upstream network(s), either because of legal reasons or local policy;
* The public key of your server (as mentioned above);
* A signed copy of the 
  [policy](https://eduvpn.org/wp-content/uploads/2019/11/eduVPN_Compliance_Statement_1.0-1.pdf)
  document by a person authorized to do so at your organization;

Use "_Add [${FQDN}] to Secure Internet eduVPN_" as "Subject" of the mail.
  
## Template

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
SAML Metadata: https://federation.example.org/metadata.xml
FQDN: vpn.example.org
Country / Region: The Netherlands
Restrictions: 
  - in/outbound tcp/25 blocked
Public Key: k7.pub.ozEaVoU0p1HezQ41.HmV1WLVuRDoPiYoa2pP0qxP1YpWdKr5AoMdV_ZWl4i4
```

Do **NOT** forget to attach the signed copy of the policy document!
