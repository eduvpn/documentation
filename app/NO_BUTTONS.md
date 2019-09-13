# Getting rid of the buttons...

We try to get rid of the app buttons where the user first has to choose 
"Institute Access" or "Secure Internet". That simply can't be explained to 
users.

## Approach

In the "first run" scenario:

1. Application opens the discovery URL, e.g. 
   `https://disco.eduvpn.org/select_idp`

2. The users chooses their IdP from a list of all available IdPs, e.g. an 
   eduGAIN WAYF;

3. The application gets the IdP identifier back through a "callback URL", e.g.
   `org.eduvpn.app://callback?IdP=https://idp.tuxed.net/metadata`;

4. The app downloads the IdP -> Server mapping from a web server to obtain the
   list of VPN servers belonging to this IdP, one file per IdP;

5. App adds the obtained server addresses to the app so the user can choose
   them afterwards;

Possible optimizations:

1. The app uses a "webview" (embedded browser window) to show the IdP list and
   obtains the user's choice

2. The app could implement their own "disco" in the app directly

## Mapping file

Obtain all available servers for IdP `https://idp.tuxed.net/metadata`: 
`https://disco.eduvpn.org/mapping/https%3A%2F%2Fidp.tuxed.net%2Fmetadata.json`.

    {
        "localServerList": [
            "https://surfnet.eduvpn.nl/"
        ],
        "guestServer": "https://nl.eduvpn.org/",
        "remoteGuestServerList": [
            "https://guest.uninett.no/",
            "..."
        ]
    }

**Format is not stable**, probably better/different names. We have to somehow 
indicate which of the guest servers is the 'primary' one for a particular IdP,
here this is the one listed in `guestServer`. The `remoteGuestServerList`
entries can be used with the token obtained form the `guestServer`.

## IdP Hint

**OPTIONAL**: the SP can decide whether or not to do this

The app typically opens the OAuth authorize URI discovered from the `info.json` 
on the server. For SAML logins it makes sense to indidicate which IdP to use
so the user does not get another IdP selector associated with the SP. We could
have a key in the `info.json` file that triggers SAML login and after that 
returns to the OAuth authorize URI

    "authorize_uri_template": "https://nl.eduvpn.org/saml/login?IdP=https://idp.surfnet.nl?return_to=@AUTHORIZE_URI@

Here the app takes the `authorize_uri_template` if it exists, constructs the 
`authorize_uri` as it would normally, and then replaces `@AUTHORIZE_URI@` with
the (url encoded) `authorize_uri`.
