# Guest Usage

One of the more unique features of this VPN service implementation is its 
ability to support "Guest Usage". This means that organizations can operate 
their own independent VPN service, while providing access to users belonging to 
other organizations without integrating their IdM, i.e. no shared user database
like LDAP. For example: students of university X can use the VPN service of 
university Y and vice versa. This is similar in spirit to 
[eduroam](https://eduroam.org/) where students and researchers of one 
university can use the WiFi network at any other participating institute. 
However, guest usage for VPNs is implemented differently, most importantly 
because of the lack of integration with an EAP supplicant on the client and to 
allow for implementations without needing a RADIUS infrastructure.

The guest usage scenario leverages the OAuth 2.0 implementation in both the VPN 
services as well as the native clients that were developed.

There are three "modes":

- Local: no guest usage is allowed, this is the default;
- Federated: guest usage is allowed by accepting tokens from a central (among 
  participants) OAuth authorization server;
- Distributed: guest usage is allowed by accepting tokens from all 
  participating VPN services.

# Federation Mode

This mode is the easiest to understand. Instead of every VPN service using 
their built-in OAuth 2.0 server, a central OAuth 2.0 authorization server is 
used by all participating VPN service where all service accepts tokens created 
by the central OAuth server.

All users MUST have the ability to authenticate to this central OAuth server. 
Typically technology such as SAML or OpenID Connect can be used for this. In 
the field of research & education an approach would be to link this central
OAuth server to eduGAIN.

The federation mode gives more control over who can authenticate, the 
authentication mechanism at the central server decides who can authenticate and
makes it possible to block users here.

# Distribution Mode

This is a slightly more complicated mode, where there is no central OAuth 
authorization server, but instead every VPN service accepts tokens from every
other VPN service, thus removing the need for a (high availability) centralized 
service.

The "distributed" mode gives the greatest flexibility. Each VPN service decides
how to authenticate its users.

# Implementation

Both "federation" and "distribution" use a "discovery" file that lists all 
participating VPN services. This is a simple static JSON file, signed by an 
(offline) asymmetric crypto key. As this JSON file is just a static file that 
contains no secrets, thus it is very easy to make this "high available" as 
there is no server side state at all. Typically participating VPN services will 
try to fetch this file periodically and accept it only after verifying the 
signature.

In case of "federated" mode this discovery file will contain the information 
about the central OAuth server, i.e. authorization endpoint and token endpoint.
In case of "distributed" mode each entry for the participating VPN services 
will also list the public key of the OAuth server for that particular VPN 
service. Thus, by fetching and verifying the signature on this file, all 
participating VPN services trust the OAuth tokens signed by the other VPN 
services.

The agreement is that all OAuth tokens are short lived, i.e. only valid for 
one hour. By requiring the VPN native application to fetch a new access token
every hour we limit the damage in case the user is no longer allowed to use the 
VPN, or an OAuth token is inadvertently leaked.

# Abuse

In order to avoid abuse, the (local) identity of the user is part of the 
OAuth token, so if abuse is detected, the identity of the user can be traced. 
If the originating VPN service uses pseudonyms instead of the "real" user 
identifier, the privacy of the user can be maintained, while allowing 
the originating VPN service to convert the pseudonym back into a "real" user
identifier if needed.
