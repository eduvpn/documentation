# Federated eduVPN

## Goal

We want to allow the users of our (mobile) eduVPN application to seamlessly 
switch between independent, NREN operated and controlled, eduVPN instances 
around the globe. We want to be able to trace abuse back to the user 
responsible, with help from the user's "home" institute, 
and to be able to effectively remediate abuse in progress.

Example: a Dutch student can choose an eduVPN endpoint in Australia just by clicking in the eduVPN app on country Australia.

## Why VPN

Having a VPN service available to use the Internet can significantly improve 
security and privacy of the user:
 
1. protect against local eavesdropping and manipulation of your traffic, e.g. 
   insecure free WiFi in a coffee shop;
2. prevent tracking of IP address by services/websites you visit;
3. prevent retaliation when using the Internet, e.g. DoS to your (home) IP;
4. circumvent state or corporate censorship, e.g. be able to use Twitter or 
   Facebook when traveling abroad in certain jurisdictions;

These features can be accomplished by running your own VPN server in the 
country of origin in a "non-federated" scenario. However, many (commercial) 
VPN providers offer their users to choose different "endpoints" in various 
countries around the world, offering additional benefits that can also be 
leveraged in the realm of research and education:

1. For researchers or journalists, research the effects of geo location, for 
   example how (web) personalization changes depending of the geo location;
2. use an endpoint in another jurisdiction because specific countries have privacy friendly legislation;
3. optimize performance, e.g. when traveling to a country on the other 
   side of the planet, connect to the "local" NREN provided VPN server instead 
   of your own NREN's server;
4. high availability: with many available endpoints in many countries, there is 
   a bigger chance of getting a connection to the VPN;

A National Research and Education Network (NREN) typically has high performance 
networks and are by nature already spread around the globe and are used to 
collaborate. the perfect place to install additional VPN nodes for a federated 
VPN model.

## Scope

Currently, the eduVPN software broadly provides two "profiles":

1. "Secure Access" is a profile to allow VPN users to connect to the 
   institute's internal network from a remote location, for example to access 
   a file share, or to perform system administration at the institute;
2. "Secure Internet" is a profile to route all the Internet traffic over the
   VPN, to be used e.g. on insecure networks like a coffee shop;

Currently, every institute has their own instance of eduVPN for both 
"Secure Access" and "Secure Internet". With the coming update to the apps, only
institutes that require "Secure Access" will get their own instance, there will
only be one "Secure Internet" instance, shared between all institutes which 
will also take care of guest usage, the goal of this proposal.

For the federation purpose, other NRENs only need to provide one 
"Secure Internet" instance that allows access from both their own member 
institutes as well as guest access.

## Current eduVPN status

Currently the eduVPN application is able to "discover" eduVPN instances by 
downloading a JSON document from a web server (registry). This file contains 
all "known" (and vetted) instances that will be shown in the application. The 
user can choose the instance they want, and have access to. 

The instances are connected to an identity federation for user 
authentication, they provide a convenient user and admin portal for both 
downloading a configuration as well as managing the instance through the web 
browser.

In addition, the eduVPN app uses OAuth to obtain an access token for a 
particular instance to e.g. obtain a VPN configuration that can then be used to 
connect to the VPN, without requiring the user to login to the portal to 
(manually) download the configuration.

All participating NRENs should deploy their own eduVPN instance with the 
"Secure Internet" profile and link it to eduGAIN. That way, the instance will 
be open for guest use!

However, for every eduVPN instance the user would need to authenticate again,
as part of the OAuth flow. So if an user already is using 'secure internet' he should re-authenticate when choosing 'secure access', because it's running on a different instance. This involves opening a web browser from within the 
application and performing authentication and authorization for every instance.

## How to implement federation

There are a number of approaches how to implement federation within eduVPN:

1. "Do nothing": leave the eduVPN design as is and connect every single eduVPN server to eduGAIN, for 
   every chosen endpoint a new OAuth credential needs to be obtained, involving 
   opening the browser, doing the OAuth dance (IdP discovery, authentication,
   authorization).;
2. Create a CA hierarchy. All (federated) eduVPN instances run under the same
   root CA by creating sub-CAs for all participating instances, which will 
   allow users of the various instances to connect to other instances;
3. Develop a central eduVPN controller node and centrally deploy and manage the VPN-nodes around the
   world;
4. Create a central OAuth server, linked to eduGAIN for user authentication 
   that provides OAuth tokens that can be used at all the instances that trust 
   this OAuth server (using public key crypto signed OAuth tokens, the public
   key could be set in the default configuration of the VPN instances); 
5. Create a registry (e.g. signed JSON document) of vetted eduVPN instances and their 
   OAuth public keys. So a key obtained at one instance can be verified by the 
   other instances.

## Benefits and Drawbacks

## 1

### Pros

* No work required in the software, already works;

### Cons

* Not so smooth user experience;
* Every eduVPN instance needs to connect to eduGAIN individually, so within eduGAIN there will be a long list of eduVPN servers per NREN;

## 2

### Pros

* Nice architecture;

### Cons

* Managing a CA is hard;
* Locks in the use of RSA, switching to better crypto, i.e. EC becomes more 
  difficult;
* Need to implement reliable CRL/OCSP as well, especially in the clients;
* Not sure if it actually works, e.g. if OpenVPN allows this kind of setup;

## 3 

### Pros

* Only one controller instance, connect it to eduGAIN and done;

### Cons

* Must have secure "backend" communication channel (2 ways) between all nodes;
* Does not allow independent operation by NRENs;
* Requires management by one party;
* No ability to leverage existing installations at NRENs;

## 4

### Pros

* Only one OAuth public key needs to be trusted by the eduVPN instances;
* Can just add IdPs from eduGAIN to OAuth server to make it work for more 
  users;
* Easier for users, they do not need to know which eduVPN their IdP is 
  connected to;
* More control over the access tokens for logging and central usage 
  information logging;

### Cons

* No need to reciprocate;
* Requires central OAuth server (potential SPoF);
* no "caching" option if the OAuth server is offline;
* need (automated) public key rollover mechanism in case the OAuth token 
  signing key needs changing (see Cons at 5);

## 5

### Pros

* Only need to update the existing registry by adding public keys as well for
  the listed instances;
* Need to reciprocate; users must be able to login (using their IdP) at at 
  least one participating eduVPN instance before they are able to use the 
  federated instances;
* eduGAIN is not required, but can be used for the federated instances if 
  wanted;
* Ability to cache the list of public keys if registry is (temporary) 
  offline;
* Signing of the registry file can be done offline for extra security;

### Cons

* Participating VPN servers need the ability to update the list of trusted
  keys, i.e. to accept newly deployed federated instances;
* Users need to know which instance, i.e. their country, their IdP is connected 
  to in order to select it first to obtain an access token to use there and 
  elsewhere;

## Analysis

We use the following (technical) criteria to evaluate the various options:

* Simple architecture;
* The least amount of possible (central) failure points;
* Maximum independence of the instances where they will continue to operate 
  in case of federation malfunction;
* Maximum flexibility, allow big freedom to operators, e.g. method of 
  user authentication;
* Must be (technically) very simple to "join" the federation;
* Encourages reciprocating, i.e. in order to "join" the federation, you need
  to provide guest access yourself as well;

So far, it seems that option 5 would fit these criteria the best, but of course
that is open for discussion, and there may be other solutions!

## Conclusion

Approach 5. With "upgrade" to approach 4. Initially option 5 is easier to 
implement, but option 4 offers some benefits that may be well worth the 
investment, due to the design of the API, switching between option 4 and 5 are
easy.
