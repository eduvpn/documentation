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

The `privateServerList` contains a list of VPN servers that are exclusivly 
available for this IdP. The access tokens for servers mentioned here are tied 
to each individual VPN server in this list.

The `publicServer` entry contains the "Home" server of users of that IdP. It 
will be used to obtain an access token that can be used at all servers 
mentioned in the `publicServerList`.

The `privateServerList` used to be the "Institute Access" servers, the 
`publicServerList` used to be the list of "Secure Internet" servers.

## IdP Hint

**OPTIONAL**: the VPN server can decide whether or not to do this

The app typically opens the OAuth authorize URI discovered from the `info.json` 
on the server. For SAML logins it makes sense to indidicate which IdP to use
so the user does not get another IdP selector associated with the SP. We could
have a key in the `info.json` file that triggers SAML login and after that 
returns to the OAuth authorize URI

    "authorize_uri_template": "https://nl.eduvpn.org/saml/login?IdP=https://idp.surfnet.nl?return_to=@AUTHORIZE_URI@

Here the app takes the `authorize_uri_template` if it exists, constructs the 
`authorize_uri` as it would normally, and then replaces `@AUTHORIZE_URI@` with
the (url encoded) `authorize_uri`.


	{
	    "api": {
	        "http://eduvpn.org/api#2": {
	            "api_base_uri": "https://vpn.tuxed.net/vpn-user-portal/api.php",
	            "authorization_endpoint": "https://vpn.tuxed.net/vpn-user-portal/_oauth/authorize",
	            "token_endpoint": "https://vpn.tuxed.net/vpn-user-portal/oauth.php/token"
	        }
	    }
	}
