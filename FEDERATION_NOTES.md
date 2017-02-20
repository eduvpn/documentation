# VPN Federation

## Why

Having a VPN service available to use the Internet has a number of features 
that make it interesting:
 
1. protect against local eavesdropping and manipulation of your traffic, e.g. 
   free WiFi in a coffee shop;
2. prevent tracking by IP address;
3. prevent retaliation when using the Internet, e.g. DoS to your (home) IP;
4. circumvent state or corporate censorship, e.g. be able to use Twitter or 
   Facebook when traveling abroad in certain jurisdictions;

These features can be accomplished by running your own VPN server in the 
country of origin in a "non-federated" scenario. However, many (commercial) 
VPN providers offer their users to choose different "endpoints" in various 
countries around the world, offering additional benefits:

1. For researchers or journalist, research the effects of geo-location, for example how adds change depending of the geo-location;
2. use an endpoint in another jurisdiction where downloading copyrighted 
   material using BitTorrent is not illegal (enough);
3. optimize performance, e.g. when traveling to a country on the other 
   side of the world, connect to a "local" VPN server instead of your home 
   institute's server;
4. high availability: with many available endpoints in many countries, there is 
   a bigger chance of getting a connection to the VPN;

A National Research and Education Network (NREN) typically has high performance 
networks and are by nature already spread around the globe and are used to 
collaborate. the perfect place to install additional VPN nodes for a federated 
VPN model.

## Tech Requirements

There are two important requirements for the federated VPN model:

1. it must be possible to "track" the user, e.g. when abuse occurs, it should
   be possible to link this back to the account of an individual;
2. it must be possible to (immediately) stop abuse when it is observed, without
   necessarily knowing the identity of the user;

Because an identity federation will be used, we assume that all users have only 
one account, that of their home institute that can be used and cannot create 
accounts at will. In some cases people could be affiliated with multiple 
institutes and then have multiple accounts. These will be treated as unrelated 
to each other.

## How

The additional benefits mentioned above can be obtained in the following ways:

1. Create a policy for NRENs to run their VPN endpoints in colleague NREN's 
   data centers around the world;
2. Have NRENs install their own VPN servers and allow "guest" usage of their 
   VPN servers, i.e. similar to "eduroam";

The first way seems very complicated from a maintenance point of view, the 
second one seems much easier. Each NREN is responsible for the own VPN servers
in their own data center and allow guest access;

Leveraging the technology behind "eduroam" would be really great, but 
unfortunately there are no (cross platform) VPN clients available that provide 
RADIUS/EAP support which makes this impossible. 
 
Fortunately, the "eduGAIN model" can be used; authentication to the (user) 
portal(s) of the VPN services provided by the participating NRENs could be done
by using SAML authentication and registering as a service provider (SP) in 
eduGAIN. That way, users or institutes that participate can use their "home" 
account to authenticate to the VPN services of other NRENs and get access to 
the VPN. 

For a user to "discover" these VPN deployments around the world, a web page 
could be created listing them all, and/or a VPN client application could be 
created listing all participating NRENs and allow the user to easily choose the 
endpoint of their choice.

## Optimization
 
The "eduGAIN model" is very clean from an architectural point of view because 
all instances are running completely independent (except for their link to 
eduGAIN). The downside however is that the user experience can be considered 
"not so smooth", since for every new NREN the user must authenticate with 
eduGAIN/SAML again for every other VPN instance. This would require opening the 
browser, potentially choose the "home" institute again and login there. 
 
There are a number of ways to improve on this, if needed:
 
1. Improve the eduGAIN/SAML flow if possible;
2. Create a CA hierarchy where each VPN provider becomes a "sub-CA" in this 
   structure;
3. Make the existing API of the participating VPN instances accept "foreign" 
   tokens to obtain access to the VPN;
4. Run one central primary controller node (with the portals) with distributed 
   VPN nodes per NREN.
 
### -1- Improve the eduGAIN/SAML flow, if possible

For many NRENs using SAML, with or without eduGAIN is their pride and glory. 
There are many services which have been eduGAIN enabled thus enabling eduVPN is
technically trivial. Important is a single sign-on experience even when choosing between eduVPN instances
located internationally. When using the eduGAIN approach the single sign-on user experience
will be strongly limited, because the session-time will expire usually within a few hours. This
forces the user to relogin when choosing another eduVPN instance. Unfortunately there is no way
to fix this, because the session-time is controlled by the Identity Provider (IdP) and not by the Service Provider (SP).

When choosing the eduGAIN scenario every single eduVPN instance has to be added to eduGAIN, which
looks odd from a eduGAIN perspective as-if they are 'competing' services. 
It makes more sense to create a federated user experience on the application layer.


## -2- Create a CA hierarchy 

This is an interesting scenario and could technically seen 'work'. It is a joint lock-in scenario 
where all NRENs work closely together and create an additional governing unit for 
maintaining the root CA. Having one (root) CA under which all server and 
client certificates are issued is a neat looking solution from an architectural 
point of view. However, it also can become quite complex: managing a CA is not 
easy. However, some of the work done in eduroam could possibly be reused in 
keeping this manageable.

### -3- Foreign API Tokens 

This is a lightweight version of the second scenario that creates less 
coupling, and the federation aspect is an add-on, that may be enabled by 
the VPN operator, but there is no hard requirement to do so. In this scenario, it is very easy to set up 
a VPN server without the need for a CA structure. Just accepting tokens from 
foreign NRENs is sufficient. 

### -4- One Central Controller Node

This is also possible, but creates a very big single point of failure, and 
doesn't give any control over the VPN nodes to the NRENs running them.

### Conclusion

It seems option 3 is the most straightforward approach to take and is our 
preferred solution.

## Implementation

The easy way to implement option 3 from above, is to create a central "token 
distribution" service that is connected to eduGAIN that allow either a central
"user portal" or (mobile) VPN apps to obtain access tokens that can be used the
API of all participating VPN services. The VPN services would verify this token 
using public key crypto and allow or reject the API call(s) to download 
configurations.

For this to work, the only change needed to the software is to configure the 
current API in the VPN services to accept foreign tokens.
