# Federation 2.0

Our initial proposal was to have a central OAuth server that issues tokens to 
users that authenticate first using an IdP registered in eduGAIN. This way, the 
VPN instances can accept tokens from this central server to allow the 
applications to interact with it. To set this up, there is a need for an OAuth 
server first, centrally managed, the users will also need to authenticate here 
and this will mean a SAML connection to eduGAIN IdPs.

Since the VPN instances all have their own OAuth server already with public 
key crypto, they could publish their public key in a central registry and 
allow any user with an access token signed by any of the published VPN server 
public keys to access their service. Instead of running a central OAuth server 
all that is needed would be a centrally managed "metadata" file containing a 
list of participating VPN servers and their OAuth public key.

All VPN instances would need to periodically fetch a copy of this file to be
able to accept users from other VPN instances. This is a weak point, if this
mechanism does not work, or is stopped, the users from newly added VPN 
instances will not get access to other instances.

A better solution would probably be a callback endpoint that the VPN services 
could use to verify a token, they do not need to update their list of 
participating VPN services, but instead could just query a server to validate
an access token for them. To this end, the access token will probably also need 
to contain the "issuer" field in order to lookup the matching public key. This 
is currently missing, but easily added. The central service is then only an 
access token validator, and not a complete OAuth server. The VPN service does 
then not revalidate the OAuth token for the duration of its lifetime.

Each VPN service provider could also "white list" VPN services that are allowed
for guest access. They could just copy/paste public keys in the server 
configuration file. This is the easiest thing to do, and maybe a good first 
step.

Another option would be to fetch public keys from a central point, so the 
public key would be fetched on first occurrence of a signed access_token with
an unknown public key. Issue with this is revoking of public keys of VPN 
services. They are typically long lived. So, the service would periodically 
need to verify if the public key is still valid, similar to CRL/OCSP. This 
seems too complex to get right...

By giving access tokens a short lifetime, e.g. 1 hour, there would be no need
to revoke the tokens. In any case, that would be no different from the central
OAuth server.


