# Session Expiry

The VPN server has the concept of "Session Expiry". This configures the 
interval with which users have to again perform application _authorization_, 
when using the eduVPN/Let's Connect! apps, or have to go back to the portal to
download a new configuration file.

This will mean that the users have to _authenticate_ as well as part of this 
authorization, and possibly provide their 2FA credentials/token as well.

The default is 90 days.

## What to Choose?

The default of 90 days, but you may want to deviate from this. Either by 
setting it to a (much) shorter interval, for example if you want your users to
authenticate every day, or possibly much longer.

Generally it is not recommended to lower this value too much if you have VPN 
users that can't use the eduVPN / Let's Connect! applications. This can lead 
to frustration of the users and possibly lead to their use of "creative" 
solutions to work around the VPN and thus decreasing security. 

On the other hand, setting this _too_ high, requires discipline to disable the
users that are no longer eligible to use the VPN from the portal.

It is a bit of a judgment call. We know of organizations that set it to 12 
hours, and also organizations that set it to 3 years.

The eduVPN / Let's Connect! applications will show the user the remaining time
of their VPN session and/or send notifications when the VPN session is about
to expire so users can choose a more convenient time to renew their session.
 
**NOTE**: if you choose to for example 1 day, this will mean that if a user
authenticates at 09:30, the next day at 09:30 their session will expire, 
meaning the may have to authorize/authenticate during a video call.

### Changing Session Expiry

You can change the session expiry by modifying 
`/etc/vpn-user-portal/config.php` and set `sessionExpiry` to the value you 
wish. Some examples:

- `P3Y` (3 years)
- `P1Y` (1 year)
- `P90D` (90 days)
- `P1M` (1 month)
- `P7D` (7 days)
- `P1D` (1 day)
- `P12H` (12 hours)

**NOTE**: if you modify this value, it will only take effect the next time the 
user is forced to authenticate/authorize.

It is *highly* recommended to choose your `sessionExpiry` and then "reset" the
server in order to make sure that all VPN users/clients will use the same 
session expiry from then on. **NOTE**: this will delete all _data_, including
local user accounts, but not the configuration. It will force everyone to 
reauthorize the VPN apps and/or download a new configuration through the 
portal.

```bash
$ sudo vpn-maint-reset-system
```

### Per User Session Expiry

**NOTE**: this has been implemented in vpn-user-portal >= 3.3.4

It is possible to allow individual `sessionExpiry` overrides based on user 
permissions. The following two are use cases we identified:

1. You want certain (power)users to be able to forgo regular 
   authentication/authorization and give them e.g. `P1Y` instead of whatever 
   the default is for your server;
2. You want certain users with access to sensitive resources to 
   authenticate/authorize e.g. every day and for instance provide their second 
   factor.

In order to configure this, make sure you follow the [ACL](ACL.md) 
documentation and set the `permissionAttributeList`, or properly configure the 
"Static" ACL.

We standardized the values required to have per user session expiry to the 
following format: `http://eduvpn.org/expiry#VALUE` where `VALUE` is one of the
_intervals_ as discussed in the previous section. Some examples:

* `http://eduvpn.org/expiry#P1Y` (1 year)
* `http://eduvpn.org/expiry#P12H` (12 hours)

**NOTE**: if 0, or >1 are provided through your IdM, the default 
`sessionExpiry` will be used.

Next, you need to enable specific values that are to be by your server. This is
done by setting the `userSessionExpiryList` next to the `sessionExpiry` field
in `/etc/vpn-user-portal/config.php`, for example:

```
'sessionExpiry' => 'P90D',
'userSessionExpiryList' => ['P1Y', 'P12H'],
```

**NOTE**: these values will only be used from the next user 
authentication/authorization and will NOT take effect immediately.
