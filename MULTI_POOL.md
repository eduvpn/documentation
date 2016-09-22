# Multi Pool

Every VPN instance supports multiple "pools". This means that every instance
can host multiple "deployment scenarios". For instance there can be two pools,
one for employees and one for network administrators. They can have completely 
different configurations, ACLs based on group membership and optionally 
two-factor authentication.

Below a configuration example is given for exactly this scenario. An 
organization has employees and administrators. The employees can access the VPN
to access the organization's resources, while the administrators can access 
additional networks to manage servers. The administrators are determined by the
ACL and have two-factor authentication enabled as to provide extra security.

We assume the instance is running as `https://vpn.example/` and was deployed 
using the provided deploy script.

**TDB**
