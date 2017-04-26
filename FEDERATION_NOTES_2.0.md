# Federation 2.0

# In the beginning...
Our initial proposal, to facilitate federated VPN usage, was to have a central OAuth server that issues tokens to 
users that authenticate first using an IdP registered in eduGAIN. This way, the 
VPN instances can accept tokens from this central server to allow the 
applications to interact with it. This requires a centrally managed OAuth 
server for which every user needs to authenticate in order to use the federated VPN functionality.
Big disadvantage is that all eduGAIN IdP's need to be SAML connected to every single eduVPN server in the world to make it work. This doesn't scale very well and requires too much day to day maitenance It would be better if we
could avoid that and organize trust in a different way.

# Federation 2.0
Since the VPN instances all have their own OAuth server already with public 
key crypto, they could publish their public key in a central registry and 
allow any user with an access token signed by any of the published VPN server 
public keys to access the services. Instead of running a central OAuth server 
all that is needed would be a centrally managed "registry" file containing a 
list of participating VPN servers and their OAuth public key.

The challenge is getting the public keys distributed to all the participating
eduVPN instances. There are a number of approaches:

1. create a list of instances and their public keys and have all instance 
   administrators manually copy/paste them in their configuration;
2. periodically fetch this list and automatically configure the listed public 
   keys;
3. On demand validation. Create a token validation service; when a token is used at any of the 
   instances, the instance will contact a central service to validate the 
   token.

We assume all access tokens have a life time of 1 hour, so we will NOT 
implement revocation. A user will need to be blocked at their "home" instance
which prevents them from getting a new valid OAuth token. In acute situations,
the particular user can directly be blocked in the admin of the instance that
is being abused.

## Considerations

The first approach is easy but requires regular manual labor, we assume that the administrator makes sure the 
public keys are correct out-of-band.

To automatically do this, the second approach, we need some kind of signature 
on the registry file (offline) signed by a trusted party. HTTPS is not 
sufficient. We have to implement a robust update mechanism.

The third approach seems a lot of work, and creates an immediate SPoF. The 
central validating service MUST always be online.

The most feasible approach is to go for the second approach by offering a JSON-file which includes the participating VPN servers and their OAuth public key.

## Discovery

The eduVPN client apps will have two discoveries. One for the "Secure Access" use case
where the VPN is used to access protected resources at an organization, and one
for the "Secure Internet" use case to access the Internet more safely.

The "Secure Access" discovery was already implemented in API 1.0 which is supported in the current Android App. 

The "Secure Internet" discovery will need to be added, where the discovery 
works exactly the same, except the user will only need to authenticate to their
"home instance", e.g. the one where their IdP is connected to:

    In which country is your home institute located?
  
    [ NL ]
    [ DE ]
    [ NO ]
    [ US ]

The user would login to their "home" instance and after that, the obtained 
access token can be used at all those instances, no need to login any more!

In addition to `instances.json` 
[example](https://static.eduvpn.nl/instances.json), we also have a 
`federation.json`:

    {
        "instances": [
            {
                "base_uri": "https://nl.eduvpn.org/",
                "display_name": "The Netherlands",
                "logo_uri": "https://static.eduvpn.org/img/nl.png",
                "public_key": "qwaWQ5LFQwuQKNQM9H0VyK9IqFimNIpPWXMtg3va3Go="
            },
            {
                "base_uri": "https://be.eduvpn.org/",
                "display_name": "Belgium",
                "logo_uri": "https://static.eduvpn.org/img/be.png",
                "public_key": "KGfKv2zBzOkpIsJzKwpQEfNy0In1ZeMam+5MJydbynQ="
            },
            {
                "base_uri": "https://no.eduvpn.org/",
                "display_name": "Norway",
                "logo_uri": "https://static.eduvpn.org/img/no.png",
                "public_key": "rHI0rYyQbUB2k2dcbNoakjo+lpGTCrzLAPe7lfYwDL4="
            },
            {
                "base_uri": "https://us.eduvpn.org/",
                "display_name": "United States of America",
                "logo_uri": "https://static.eduvpn.org/img/us.png",
                "public_key": "AS8X/Iz1o6XDe6oFm0UxvYZhljaAnWz4YtAOr06Q/vw="
            },
        ],
        "version": 1
    }

The `public_key` field is used by the federated instances to know the public
key of the other instances, it is not used by the application.
