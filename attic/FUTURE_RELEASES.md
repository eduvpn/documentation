# Future Releases

This is a rough plan for future development of the eduVPN code. If the features
are listed under 1.X they can be implemented without breaking existing 
installations or requiring (configuration) updates to it.

# 1.X

* use only 1 URL for triggering SAML authentication, set cookie there for 
  keeping the session, the upgrade path may be a bit tricky as the Apache 
  configuration may need modification (requires investigation);
* allow for client generated certificates (CSR) instead of server generated;

# 2.X

For a 2.X release it is allowed to break compatibility with existing deploys. A
script will be provided to upgrade 1.X installations. 

* merge `vpn-user-portal`, `vpn-admin-portal` and `vpn-server-api` to simplify
  architecture;
  * simplifies install and removes the need for extensive internal/private 
    API;
* think about making "multi instance" deploys work better, currently it is
  * too complicated (potential security risks!);
  * no IPv6 (outer tunnel) support in these kinds of deploys;
* get rid of `info.json` and instead use convention over configuration;
* maybe get rid of `vpn-user-portal` functionality, instead use client that 
  uses API and supports all instances;
* move OpenVPN status/kill to `vpn-server-node` away from `vpn-server-api`;
* get rid of VPN/private network requirement for talking to `vpn-server-node`, 
  use API instead (maybe HTTP, or something else)
