# VPN Federation
 
Having a VPN service available to use the Internet has a number of features 
that make it interesting:
 
1. protect against local eavesdropping on your connection, e.g. free WiFi in a 
   coffee shop;
2. "hide your IP" to have the ability to not show your "real" IP to services 
   you use;
3. circumvent state or corporate censorship, e.g. blocking of Pirate Bay in The 
   Netherlands by many ISPs at some point;
4. circumvent geo-restricted content that is only available for a select 
   audience, e.g. national public broadcasting organizations (like BBC and 
   NOS), Netflix, Google and Apple stores.

Running a (local) VPN service typically gives the users only the first two 
benefits. However, many (commercial) VPN providers install servers in data 
centers all around the world to be able to provide benefits 3 and 4. In 
addition it allows the user to choose an endpoint close to their own location
and thus reducing the latency.

Within the National Research and Education Network (NREN) community, there 
are a number of approaches that will allow for optimizing the common commercial 
VPN provider approach. NREN's are by nature already spread around the globe and
are used to collaborate. Two approaches are feasible:
 
1. Allow NREN in country X to run (virtual/containerized) VPN machines in the 
   data center(s) of NREN in country Y and vice versa;
2. Create a (federated) model where each NREN runs their own VPN service, but 
   allow users of all participating NRENs to use all instances.
 
Both those scenarios are plausible, however the first scenario requires a lot 
of maintenance and central monitoring in (possibly) foreign data centers. This can 
probably partly be automated, but seems best avoided. The second scenario where 
an NREN is only responsible for their own servers in their own data center(s) 
while allowing "guest" access seems preferable.
 
The second approach already has services that follow this model:
 
1. eduroam for accessing wireless networks in other countries operated by other 
   NRENs or their members using the "home" credentials;
2. eduGAIN for (federated) SAML web based authentication where a user can use 
   their "home" credentials to authenticate to service providers.
 
Using the "eduroam model" would require the use of RADIUS to handle the 
user credentials in a secure fashion. This would be a great approach, but 
unfortunately there are no (cross platform) VPN clients available that provide 
this functionality.
 
The "eduGAIN model" can be used; authentication to the (user) portal(s) of the 
VPN services provided by the participating NRENs could be done by using SAML 
authentication and registering as a service provider (SP) in eduGAIN. That way, 
users or institutes that participate can use  their "home" account to 
authenticate to the VPN services of other NRENs and get access to the VPN. 
Using an "app" can reduce confusion by just listing all VPN services (or their
endpoints in various countries) and using an API to transparently obtain 
configurations when needed.

# Optimization
 
The "eduGAIN model" is very clean from an architectural point of view because 
all instances are running completely independent. The downside however is that 
the user experience can be considered "not so smooth", since for every new 
country/NREN the user must authenticate with eduGAIN/SAML again for every other 
eduVPN server. This would require opening the browser, potentially choose the 
"home" institute again and login there. Although this needs to happen only once 
per country/NREN, it is not so "smooth" for the user. To be fair, users have 
been trained to do just this for many years now, so it may not be such a big 
deal.
 
We could envision a number of optmizations:
 
1. Improve the eduGAIN/SAML flow to make it less of a hassle for the user;
2. Create a CA structure where each VPN provider becomes a "sub-CA" in this 
   structure;
3. Make the existing API of the participating VPN instances accept "foreign" 
   tokens to obtain access to the VPN;
4. Run one central primary controller node (with the portals) with distibuted 
   VPN nodes per NREN.
 
For many NRENs using SAML, with or without eduGAIN is their pride and glory. 
Working around its limitations seems weaselly. Instead of fixing the user 
experience (UX), we'd be working around it. That in itself could be seen as a 
good reason to go with this solution and improve the UX for the users. Not 
choosing this path could be seen as admitting defeat when considering the UX 
for SAML authentications.
 
The second scenario is interesting and could totally work. It is the perfect 
lock-in scenario where all NRENs work together and create an additional 
governing unit for maintaining the root CA. Having one (root) CA under which 
all server and client certificates are issued is a neat looking solution from 
an architectural point of view. However, it also can become quite complex: 
managing a CA is not easy. However, some of the work done in eduroam could 
possibly be reused in keeping this manageable.
 
The third solution is a lightweight version of the second scenario that creates 
less coupling, and there the federation aspect is an add-on, that can be 
enabled by the server operators, but doesn't need to. This way, it is very 
easy to set up a VPN server without requiring (CA) signing. Just accepting 
tokens from foreign NRENs is sufficient. 

The fourth option is also possible, but creates a very big single point of 
failure, and doesn't give any control over the VPN nodes to the NRENs running
them.

So, it seems option 3 is the most straightforward approach to take and is our
preferred solution.

# Implementation

The easy way to implement option 3 from above, is to create a central "token 
distribution" service that is connected to eduGAIN that allow VPN apps to 
obtain an access token that can be used at all VPN services. The VPN services 
would verify this token using public key crypto and allow or reject the API 
call(s) to download configurations.

For this to work, the only change needed is to configure the current API in the
VPN services to accept foreign tokens.

# Abuse
 
User X of NREN Y abusing the VPN service of NREN Z can be blocked based on 
their user ID in the foreign token. The user cannot circumvent this as the 
same VPN service will always see the same user ID for that particular user
("persistent ID"), so unless the user has the ability to create multiple user 
accounts, something federation policies should prevent) this should work out 
fine.

If there is a "serious" problem, a procedure could be created to map the user 
ID the VPN service received to a "real" user inside the federation. This will
not be automated and will require cooperation from the central token service. 
This would also make it possible to block the user from using the VPN at all.

The important thing is that the NREN running the VPN service has control of 
(permanently) blocking a particular user from using their service.
