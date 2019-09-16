# Getting rid of the buttons...

We are trying to get rid of the "use case" buttons in the eduVPN apps. 
Currently the user first has to choose "Institute Access" or "Secure Internet". 
This is not easy to explain to users. It would be better when users can simply
select their institute from a list, like they are already used to from the 
existing identity federations.

The advantage here is that the user does not have to choose from a list of 
VPN servers that don't necessarily have a (direct) link to their IdP.

## User Flow

In the "first run" scenario:

1. The user opens the application;

2. The user chooses their IdP

3. The app shows the available VPN servers linked to that particular IdP, 
   e.g. a VPN server for "Institute Access" and a list of VPNs around the 
   world that can be used for "Secure Internet".
   
The app stores the IdP the user chooses so this IdP selector step does not 
need to be repeated anymore. 

On subsequent runs the app immediately shows VPN 
servers as obtained/configured during the last run.

## App Flow

In the "first run" scenario:

1. Application opens the IdP discovery URL either in an external browser or in 
   an embedded "Web View"; 
   
2. The users chooses their IdP from a list of all available IdPs, e.g. an 
   eduGAIN WAYF;

3. The application gets the IdP identifier back through a "callback URL", e.g.
   `org.eduvpn.app://callback?IdP=https://idp.tuxed.net/metadata`, the app can
   either register this scheme, or obtain the redirect URI from the Web View 
   control(s);

4. The app downloads the IdP -> Server mapping from a web server to obtain the
   list of VPN servers the chosen IdP has access to;

5. The app adds the obtained server addresses to the app so the user can choose
   them afterwards;

### Notes

* The app MUST allow for forgetting the chosen IdP;
* The app MUST NOT contact the network unless the user tries to add a new VPN 
  server, or tries to connect to an existing one;

## Mapping file

**NOTE**: mapping file format is NOT stable

Obtain all available servers for an IdP by querying the central server, e.g. 
for the IdP `https://idp.tuxed.net/metadata` one would query 
`https://disco.eduvpn.org/mapping/https%3A%2F%2Fidp.tuxed.net%2Fmetadata.json`.

    {
        "privateServerList": [
            "https://surfnet.eduvpn.nl/"
        ],
        "publicServer": "https://nl.eduvpn.org/",
        "publicServerList": [
            "https://guest.uninett.no/",
            "..."
        ]
    }

The `privateServerList` contains a list of VPN servers that are exclusively 
available for this IdP. The access tokens for servers mentioned here are tied 
to each individual VPN server in this list.

The `publicServer` entry contains the "Home" server of users of that IdP. It 
will be used to obtain an access token that can be used at all servers 
mentioned in the `publicServerList`.

The `privateServerList` used to be the "Institute Access" servers, the 
`publicServerList` used to be the list of "Secure Internet" servers.

## IdP Hint

Many (all?) servers that want to provide "Guest Usage" are linked to SAML 
federations. If the discovery of the user's IdP is moved to the application 
itself, opening the OAuth authorization URL may trigger another "WAYF" from 
the identify federation. 

In order to avoid the user having to choose their IdP twice, it makes sense to
be able to provide an IdP hint to the VPN server and avoid the WAYF.

OAuth does not provide a mechanism for this directly, OIDC would, but we do not
exclusively use OIDC, so we need something "vendor independent" to open the 
correct URL.

How to this exactly depends on the SAML implementation chosen by the VPN 
server. As the VPN app has no knowledge of the used authentication mechanism, 
we can provide some kind of "IdP hint". 

Typically, an SP uses the "Identity Provider Discovery Service Protocol and 
Profile". This means that a WAYF, after the user selects the IdP, returns 
to the SP. By using a special URL, we can already "choose" for the user based
on the IdP the user chose in the eduVPN app, and use the OAuth "authorize URI"
as the `return` or `ReturnTo` parameter.

For example, for `vpn.tuxed.net` the following URL can be used to trigger a 
login using the IdP `https://idp.tuxed.net/metadata` and `ReturnTo` the OAuth 
authorization URL, skipping the VPN server WAYF:

    https://vpn.tuxed.net/vpn-user-portal/_saml/login?ReturnTo=https%3A%2F%2Fvpn.tuxed.net%2Fvpn-user-portal%2F_oauth%2Fauthorize%3Fclient_id%3Dorg.eduvpn.app.windows%26redirect_uri%3Dhttp%3A%2F%2F127.0.0.1%3A12345%2Fcallback%26response_type%3Dcode%26scope%3Dconfig%26state%3D12345%26code_challenge_method%3DS256%26code_challenge%3DE9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&IdP=https%3A%2F%2Fidp.tuxed.net%2Fmetadata

A mechanism exist to tell the app about server specific configurations, i.e. 
the `info.json` file. We can add a special key there that provides a template 
for the application to use. For example, the template for the above URL could
be:

    https://vpn.tuxed.net/vpn-user-portal/_saml/login?ReturnTo=@AUTHORIZE_URI@&IdP=@IDP_ENTITY_ID@

This template URL will depend on the SAML software used at the SP, and 
also on the host name of the VPN server. 

**NOTE**: the `@AUTHORIZE_URI@` MUST be already URL encoded before being used 
as a replacement for the `@AUTHORIZE_URI@` string!
