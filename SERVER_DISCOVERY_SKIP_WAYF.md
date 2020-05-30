# Skipping the SAML WAYF

This builds on [SERVER_DISCOVERY](SERVER_DISCOVERY.md).

Most "Secure Internet" servers use SAML to authenticate the users and have a 
WAYF (Where Are You From) to redirect users to the IdP chosen by the user for 
the actual authentication. As we already have a "WAYF" in the eduVPN 
application, there is no need to have the user select their institute again in 
the browser.

**NOTE**: this ONLY applies to "Secure Internet" servers!

This document explains how to have the WAYF skipped during the SAML 
authentication. This is possible because the user _already_ selected their 
organization in the application. There is no need to ask for it again.

Most SAML SPs have some means to trigger authentication directly by going to
some URL and provide the `IdP` and `ReturnTo` parameters indicating which IdP 
to use and where to go _after_ authentication.

As OAuth is used by the VPN application, the OAuth "authorization URL" needs to
be placed in the `ReturnTo` query parameter instead of opening it directly. The
`organization_list.json` contains a list of organizations and the `org_id` key
that is the hint for skipping the WAYF. When SAML is used, the `org_id` is 
typically the "entityID" of the SAML IdP and can be used as the `IdP` query
parameter.

Unfortunately, there are (at least) three types of SAML federations:

1. Full mesh federation: all IdPs know about all SPs and the other way around;
2. Hub/proxy federation: all IdPs are behind a SAML proxy and every IdP and SP
   only talk to the proxy;
3. One IdP scenario: there is one IdP that is used by all organizations, 
   only [Feide](https://www.feide.no/) is of this type as far as I know.

So depending on the type of federation and/or SAML SP software that is used by
the VPN server we need to approach things differently.

The `server_list.json` file MAY contain a key `authentication_url_template` for
"Secure Internet" servers that contains a specific URL template for the server 
involved in order to properly "skip the WAYF".

When the user chooses an organization that has a `secure_internet_home` 
pointing to one of these servers the `org_id` of the chosen organization is 
remembered. Together with this `org_id` and the constructed OAuth 
authorization URL, the `authentication_url_template` is used to construct a URL 
that will be opened in the browser.

For example, the `https://nl.eduvpn.org/` server has the following 
`authentication_url_template`:

    https://nl.eduvpn.org/php-saml-sp/login?ReturnTo=@RETURN_TO@&IdP=@ORG_ID@

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
