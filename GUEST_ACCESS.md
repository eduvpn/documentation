# Guest Access

This document describes how to enable "Guest Access". This is a feature 
provided to the eduVPN community. It is NOT available for Let's Connect!.

Participating NRENs configure an eduVPN server to allow users from 
servers hosted by other NRENs to access their VPN server as well. 

This means for example that a user from the eduVPN server hosted in The
Netherlands by SURF can access the VPN server in Germany hosted by DFN.

**NOTE**: the "Guest Access" server MUST be a server dedicated ONLY for 
this purpose. It MUST NOT be used for any other purpose like providing 
access to restricted resources on the network!

## Eligibility / Requirements

Only NRENs are able to register a server for "Guest Access". We MAY request a
introduction (video) call if none of the eduVPN team has met you before.

You MUST use SAML authentication for your VPN server and provide us 
with a link to the SAML metadata for all IdPs (Identity Providers) that
have access to your server. We need this information to populate the 
organizations list in the eduVPN applications. Without SAML
metadata URL you can still participate, but your local users won't be
able to access any of the other "Guest Access" servers.

Currently we do NOT recommend registering your VPN server in eduGAIN!

In order to enable "Guest Access" on your server you MUST have 
`vpn-user-portal` >= 3.1. In older versions it will NOT work.

## Configuration

The "Guest Access" functionality MUST be manually enabled.

You need to edit `/etc/vpn-user-portal/config.php` and modify the `Api` 
section:

```php
'Api' => [
	'enableGuestAccess' => true,
]
```

After enabling "Guest Access" you **MUST** reset your server to remove all 
data. With "Guest Access" enabled you'll get new "User IDs" which will break
e.g. OAuth. With this reset you'll delete all existing user accounts, 
invalidate all VPN configurations and associated OAuth authorizations.

```bash
$ sudo vpn-maint-reset-system
```

Next you need to generate a HMAC key that will be used to "obfuscate" the user 
identifiers of your users as to not "leak" them to other NREN servers.

```bash
$ sudo /usr/libexec/vpn-user-portal/generate-secrets --hmac
```

If you were using the `adminUserIdList` option in 
`/etc/vpn-user-portal/config.php` to list your admins, you MUST update them to 
list the new "User IDs". Have your admins look on their "Account" page in the
portal so you can add them. For more information on admin accounts you can 
look [here](PORTAL_ADMIN.md).

## Public Key

We need to register your OAuth public key in our "discovery" file 
to allow all participating servers to fetch it and allow users from
your VPN service.

You can find this Public Key by going to the "Info" tab,  with an admin 
account, in your VPN portal. Expand the "Server" section by clicking "More" and 
look for "Public Key" under "OAuth". It has the following form:

```
k7.pub.ozEaVoU0p1HezQ41.HmV1WLVuRDoPiYoa2pP0qxP1YpWdKr5AoMdV_ZWl4i4
```

Make note of this public key as you need it for your server's registration.

## Registration

Please contact 
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org) and 
provide use with the following information:

* A *generic* contact email address to be contacted for general inquiries, to 
  be listed on the [Participants](https://www.eduvpn.org/countries/) page;
* An *abuse* contact email address to be contacted in case of abuse (preferably 
  a role-based mail address);
* A *technical* contact email address to be contacted in case of technical 
  problems, i.e. that reaches the operators/maintainers of the VPN server(s), 
  preferably a role-based mail address;
* End-user support contact(s), at least one of: mail, URL, phone number.
  **NOTE** these will become public;
* A web site we can refer end-users to for this particular _Secure Internet_ 
  server (Optional);
* The SAML metadata URL that contains all the organizations that have access 
  to your server which will be used to populate the eduVPN applications, i.e. 
  the **IdP** (federation) metadata URL;
* The full hostname (FQDN) of your VPN server;
* Make sure TLS is configured properly! Use e.g. 
  [SSL Server Test](https://www.ssllabs.com/ssltest/);
* The name of the country / region your VPN server is located in (English);
* Full information on any filtering/blocking of traffic by your VPN server or 
  upstream network(s), either because of legal reasons or local policy;
* The public key of your server (as mentioned above);
* A signed copy of the 
  [policy](https://eduvpn.org/wp-content/uploads/2019/11/eduVPN_Compliance_Statement_1.0-1.pdf)
  document by a person authorized to do so at your organization;

Use "_Add [${FQDN}] to Secure Internet eduVPN_" as "Subject" of the mail.
  
### Template

Subject: `Add [vpn.example.org] to Secure Internet eduVPN`

Body:
```
Generic Contact: admin@example.org
Abuse Contact: abuse@example.org
Technical Contact: eduvpn@example.org
End-user Support Contact: 
  - support@example.org
  - +1234567890
  - https://support.example.org/
Information Website: https://www.example.org/services/eduvpn
SAML Metadata: https://federation.example.org/metadata.xml
FQDN: vpn.example.org
Country / Region: The Netherlands
Restrictions: 
  - in/outbound tcp/25 blocked
Public Key: k7.pub.ozEaVoU0p1HezQ41.HmV1WLVuRDoPiYoa2pP0qxP1YpWdKr5AoMdV_ZWl4i4
```

Do **NOT** forget to attach the signed copy of the policy document!

## Usage

Once deployed, it may be interesting to figure out whether your service is used
and by whom.

### Guest Users

To show how many guest users there are, you can use the including tooling, 
e.g.:

```bash
$ sudo vpn-user-portal-account --list | grep '@' | cut -d '@' -f 2 | sort | uniq -c | sort -n -r
     38 eduvpn1.eduvpn.de
      8 eduvpn.deic.dk
      7 eduvpn.ac.lk
      4 eduvpn1.funet.fi
      3 eduvpn.uran.ua
      2 vpn.pern.edu.pk
      2 guest.eduvpn.ac.za
      1 eduvpn.eenet.ee
```

Here you can see how many *unique* users arrive from a particular other 
country. Of course you could have also seen that on the portal's "Users" tab, 
but this makes it easier to automatically count them.

If you are more interested in getting results about the actual use on a 
particular date, you can try this:

```bash
$ sudo sqlite3 \
    /var/lib/vpn-user-portal/db.sqlite \
    "SELECT DATE(connected_at) AS date, COUNT(DISTINCT user_id) as unique_guest_user_count FROM connection_log WHERE user_id LIKE '%@%' GROUP BY date ORDER BY connected_at"
```

### Local Users

When "Guest Access" is enabled, and you also have local users, you can also 
figure out who they are, depending on your server's configuration. For example,
if you use [Shibboleth](SHIBBOLETH_SP.md) for user authentication, and you use 
the `eduPersonTargetedID` attribute (or any other that contains the domain 
(or scope) of the organization the user originates from) you can do this.

When "Guest Access" is enabled, a "pseudonymous" identifier is generated for 
each user account and the original identifier is stored in the `auth_data` 
column of the `users` table as JSON. This is done as to not "leak" the local 
user identifier to other servers.

When using the `eduPersonTargetedID` attribute, the value has the format 
`${IDP_ENTITY_ID}!${SP_ENTITY_ID}!${USER_ID}`, for example 
`http://login.surf.nl/adfs/services/trust!https://nl.eduvpn.org/saml!588b17cf3a31012abb4860ae6faf440b6da006fe`.

Now to figure out which "IdPs" are used and by how many users, we can query 
the database:

```bash
$ sudo sqlite3 \
    /var/lib/vpn-user-portal/db.sqlite \
    "SELECT json_extract(auth_data, '$.userId') FROM users WHERE user_id NOT LIKE '%@%'" \
    | cut -d '!' -f 1 \
    | sort \
    | uniq -c \
    | sort -r -n
```

This will output IdPs used together with how many users of each IdP used the 
service.
