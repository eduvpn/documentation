# Admin API

**WORK IN PROGRESS**

We provide an Admin API that can be used by administrators to "bulk" create and 
destroy VPN configurations for users.

This is useful for example when you want to provision managed devices with a 
VPN configuration without having your users configure the VPN.

The API can be used to obtain WireGuard or OpenVPN configuration files that 
are ready to use with the OpenVPN and WireGuard VPN clients.

**NOTE**: this describes a **PREVIEW** feature. We aim to fully support this 
feature starting from server version >= 3.1. Please test and provide us with 
feedback if you want to use this feature to make sure it satisfies your 
requirements! Be aware that you MAY need to update your configuration when 
using this feature before we consider this feature stable! The more feedback we 
get, the better!

# Configuration

The Admin API is _disabled_ by default, but it is easy to enable.

**TODO**: document how to enable it

The _secret_ can be found in `/etc/vpn-user-portal/keys/admin-api.key`. Use 
this value in the `Authorization` (Bearer) header.

# API Calls

**TODO**: think about names of API 

We currently have two API calls, `/create` and `/destroy` that can be used to
create a VPN configuration for a particular user and to remove the VPN 
configurations of a particular user.

| Parameter      | Required | Value(s)                                                                         |
| -------------- | -------- | -------------------------------------------------------------------------------- |
| `user_id`      | Yes      | The user for which to create the configuration                                   |
| `display_name` | No       | How to list the created configuration in the portal (default: `Admin API`)       |
| `profile_id`   | Yes      | The `profile_id` of the VPN profile to create a configuration for                |
| `public_key`   | No       | A WireGuard public key, for the WireGuard protocol                               |
| `prefer_tcp`   | No       | Prefer connecting over TCP to the server. Either `yes` or `no`. Defaults to `no` |

## Create

### Request

Connect to the "Employees" profile (`employees`) and specify a WireGuard public 
key for when WireGuard will be used:

```bash
$ curl \
    -d "user_id=foo" \
    -d "profile_id=employees" \
    --data-urlencode "display_name=Admin API Example Config" \
    --data-urlencode "public_key=nmZ5ExqRpLgJV9yWKlaC7KQ7EAN7eRJ4XBz9eHJPmUU=" \
    -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/admin/v1/create"
```

## Destroy

**TODO**: also need `profile_id` to only delete config of certain profile?

```bash
$ curl \
    -d "user_id=foo" \
    -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/admin/v1/destroy"
```
