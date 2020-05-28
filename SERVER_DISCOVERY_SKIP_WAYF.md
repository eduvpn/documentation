# Skipping the SAML WAYF

This builds on [SERVER_DISCOVERY](SERVER_DISCOVERY.md).

Most "Secure Internet" servers have their own WAYF to redirect users to the 
relevant IdP for the actual authentication. As we already have a "WAYF" in the
eduVPN application, there is no need to have the user select their institute
again in the browser.

This document talks about how to "Skip" the WAYF in the browser.

Most SAML SPs have some means to trigger authentication directly by going to a
URL and provide the `IdP` and `ReturnTo` parameters indicating which IdP to use
and where to go _after_ authentication.

As OAuth is used by the VPN application, the OAuth "authorization URL" needs to
be placed in the `ReturnTo` query parameter instead of opening it directly. The
IdP we the user chose we already know from the organization the user chose in 
the application by `org_id`. This `org_id` is typically the entity ID of the
IdP and can thus be used as the `IdP` query parameter value.

Unfortunately, there are (at least) three types of SAML federations:

1. Full mesh federation: all IdPs know about all SPs and the other way around;
2. Hub/proxy federation: all IdPs are behind a SAML proxy and every IdP and SP
   only talk to the proxy;
3. One IdP scenario: there is one IdP that is used by all organizations, 
   only [Feide](https://www.feide.no/) is of this type as far as I know.

So depending on the type of federation and/or SAML SP software that is used by
the VPN server we need to approach things differently.

The following servers are supported for "skipping the WAYF":

| `baseUrl`                    | Authentication URL Template                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| `https://nl.eduvpn.org/`     | `https://nl.eduvpn.org/php-saml-sp/login?ReturnTo=@RETURN_TO@&IdP=@ORG_ID@`          |
| `https://eduvpn1.eduvpn.de/` | `https://eduvpn1.eduvpn.de/saml/login?ReturnTo=@RETURN_TO@&IdP=@ORG_ID@`             |
| `https://eduvpn1.funet.fi/`  | `https://eduvpn1.funet.fi/Shibboleth.sso/Login?entityID=@ORG_ID@&target=@RETURN_TO@` |

When the user chooses an organization that has a `secure_internet_home` 
pointing to one of these servers the `org_id` of the chosen organization is 
remembered. Together with this `org_id` and the constructed OAuth 
authorization URL the template URL is used to construct a URL that will be 
opened in the browser.

The string `@RETURN_TO@` is replaced by the URL encoded value of the OAuth 
authorization URL. The string `@ORG_ID@` is replaced by the URL encoded value
of `org_id`.

Example:

| Query Parameter | Value
| --------------- | ----
| `IdP`           | `https://idp.surfnet.nl`
| `ReturnTo`      | `https://nl.eduvpn.org/portal/_oauth/authorize?client_id=net.tuxed.vpn-for-web&redirect_uri=https%3A%2F%2Fvpn.tuxed.net%2Fvpn-for-web%2Fcallback&scope=config&state=GZ885EVj8rZrjfp589Euyusppz1UhdUovGgpEZJi3Q0&response_type=code&code_challenge_method=S256&code_challenge=lViGPZrGwiV4-dDI2KL-UpbQ-jSwHHeUU4HhfmZTBF0`

The full URL after using the template thus becomes: `https://nl.eduvpn.org/php-saml-sp/login?ReturnTo=https%3A%2F%2Fnl.eduvpn.org%2Fportal%2F_oauth%2Fauthorize%3Fclient_id%3Dnet.tuxed.vpn-for-web%26redirect_uri%3Dhttps%253A%252F%252Fvpn.tuxed.net%252Fvpn-for-web%252Fcallback%26scope%3Dconfig%26state%3DGZ885EVj8rZrjfp589Euyusppz1UhdUovGgpEZJi3Q0%26response_type%3Dcode%26code_challenge_method%3DS256%26code_challenge%3DlViGPZrGwiV4-dDI2KL-UpbQ-jSwHHeUU4HhfmZTBF0&IdP=https%3A%2F%2Fidp.surfnet.nl`.

When opening the browser with this, the authentication is performed using the 
specified IdP and after authentication the OAuth authorization is started thus
skipping the "WAYF" in the browser.

# Open Issues

With SAML proxies we somehow need to indicate which IdP is to be used. This can
typically be done using `AuthnRequest` "scoping". The SP needs to support this
through a query parameter.

It _may_ work through clever `ReturnTo` (double) encoding.

With Feide we need to be even more clever as `AuthnRequest` "scoping" may not 
be supported (unconfirmed as of 2020-05-26). There we may not have any other 
choice than be clever `ReturnTo` (double) encoding.

# Triggering SAML Login through URL

## Mellon

[Documentation](https://github.com/latchset/mod_auth_mellon#manual-login)

- `ReturnTo`
- `IdP`

URL format: `/saml/login?ReturnTo=X&IdP=Y`

## Shibboleth

[Documentation](https://wiki.shibboleth.net/confluence/display/SP3/SessionInitiator#SessionInitiator-InitiatorProtocol)

- `target`
- `entityID`

URL format: `https://sp.example.org/Shibboleth.sso/Login?target=https%3A%2F%2Fsp.example.org%2Fresource.asp&entityID=https%3A%2F%2Fidp.example.org%2Fidp%2Fshibboleth`

## simpleSAMLphp

See [this](https://github.com/simplesamlphp/simplesamlphp/blob/master/modules/core/www/as_login.php). Seems `saml:idp` is not documented...

- `ReturnTo`
- `AuthId`
- `saml:idp`

URL format: `/simplesaml/module.php/core/as_login.php?AuthId=<authentication source>&ReturnTo=<return URL>`

## php-saml-sp

- `ReturnTo`
- `IdP`

URL format: `/php-saml-sp/login?ReturnTo=X&IdP=Y`
