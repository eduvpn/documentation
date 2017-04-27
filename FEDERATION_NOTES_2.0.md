# Federation 2.0

## Previously...

In our initial proposal, in order to facilitate federated VPN usage, we 
envisioned a central OAuth server that issues tokens to the (mobile) 
applications. The instances of eduVPN, located around the world, could then 
accept access tokens from this OAuth server. Applications would only need to 
obtain one access token that could be used at all federated instances.

This has a number of disadvantages:

* We need to operate a central OAuth authorization server;
* All IdPs of all involved federations need to be connected to this OAuth 
  server using eduGAIN;

It would be better if we could avoid that and organize trust in a different 
way.

## And Now...

Since the VPN instances all have their own OAuth server already with public 
key crypto, they could publish their public key in a registry and allow any 
user with an access token signed by any of the published VPN server public 
keys to access the services. Instead of running a central OAuth server 
all that is needed would be a managed "registry" file containing a list of 
participating VPN servers and their OAuth public key.

The challenge is getting the public keys distributed to all the participating
eduVPN instances. There are a number of approaches:

1. Create a list of instances and their public keys and have all instance 
   administrators manually copy/paste them in their configuration;
2. Periodically fetch this list and automatically configure the listed public 
   keys;
3. On demand validation. Create a token validation service; when a token is 
   used at any of the instances, the instance will contact a central service to 
   validate the token.

We assume all access tokens have a life time of 1 hour, so we will NOT 
implement revocation. A user will need to be blocked at their "home" instance
which prevents them from getting a new valid OAuth token. In acute situations,
the particular user can directly be blocked in the admin of the instance that
is being abused using the admin portal.

### Considerations

The first approach is relatively easy but requires regular manual labor, we 
would assume that the administrator makes sure the public keys are correct 
out-of-band.

To automatically do this, which would be the second approach, we need some kind 
of signature on the registry file (offline) signed by a trusted party. HTTPS is 
not sufficient. In addition we have to implement a robust update mechanism.

The third approach seems a lot of work, and creates an immediate SPoF. The 
central validating service MUST always be online. It is not much different from
the central OAuth server in the previous proposal.

The most feasible approach seems to be to go for the second approach by 
providing a JSON-file which contains a list of the participating VPN instances 
and their OAuth public keys.

### Discovery

The eduVPN client apps will have two discoveries. One for the "Secure Access" 
use case where the VPN is used to access protected resources at the user's 
organization, and one for the "Secure Internet" use case to access the 
Internet more safely. For the federation use case, we talk about the 
"Secure Internet" use case.

The "Secure Access" discovery was already part of the initial application 
design, this is currently supported by the Android App. 

The "Secure Internet" discovery works exactly the same as with "Secure Access", 
except there is only one instance the application will need to obtain an 
access token.

    In which country is your institution (IdP) located?
  
    [ NL ]
    [ DE ]
    [ NO ]
    [ US ]

This would select the eduVPN instance that is operated by the NREN in that 
particular country to which the user's IdP is connected. There is no longer the
need for eduGAIN to connect IdPs to eduVPN instances. Only IdPs belonging to
the NRENs will be connected to that eduVPN instance.

The user would login to their NRENs instance and after that, the obtained 
access token can be used at all the instances, no need to obtain additional 
tokens anymore!

In addition to `instances.json` 
[example](https://static.eduvpn.nl/instances.json) for the "Secure Access" use
case, we also have a `federation.json` for the "Secure Internet" use case:

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

### Optimization

If one application is used for both "Secure Access" and "Secure Internet", e.g. 
the federated use case, the user could be offered to choose their IdP on first 
use of the application, so as far as "IdP discovery" goes, this would need to 
be done only once.
