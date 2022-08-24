# Admin API

**WORK IN PROGRESS**

We provide an API that can be used by administrators to create and destroy VPN 
configurations for users. This can be useful when organizations want to 
_provision_ managed devices with a VPN configuration, _without_ having their 
users manually configure the VPN.

The API can be used to obtain WireGuard or OpenVPN configuration files that 
are ready to use with the official OpenVPN and WireGuard VPN clients. There 
would be no need to use the eduVPN or Let's Connect! applications in this 
scenario.

**NOTE**: this is a [Preview Feature](PREVIEW_FEATURES.md)!

# Configuration

The API is _disabled_ by default, but it is easy to enable.

```bash
$ sudo /usr/libexec/vpn-user-portal/generate-secrets --admin-api
```

By default, the API is only accessible from `localhost` in order to avoid 
anyone accessing the API from the network.

You can modify `/etc/httpd/conf.d/vpn-user-portal.conf` on Fedora/EL, or 
`/etc/apache2/conf-available/vpn-user-portal.conf` on Debian/Ubuntu. Do NOT 
forget to restart Apache after modifying the files.

In order to use the API, the _secret_ you need can be found in 
`/etc/vpn-user-portal/keys/admin-api.key` after generating it which was done
above. Use this value in the `Authorization` (Bearer) header. See the examples
below.

# API Calls

We currently have two API calls, `/create` and `/destroy` that can be used to
create a VPN configuration for a particular user and to remove the VPN 
configurations of a particular user.

## Create

| Parameter      | Required | Value(s)                                                                         |
| -------------- | -------- | -------------------------------------------------------------------------------- |
| `user_id`      | Yes      | The user for which to create the configuration                                   |
| `display_name` | No       | How to list the created configuration in the portal (default: `Admin API`)       |
| `profile_id`   | Yes      | The `profile_id` of the VPN profile to create a configuration for                |
| `prefer_tcp`   | No       | Prefer connecting over TCP to the server. Either `yes` or `no`. Defaults to `no` |

### Request

Connect to the "Employees" profile (`employees`) and specify a WireGuard public 
key for when WireGuard will be used:

```bash
$ curl \
    -d "user_id=foo" \
    -d "profile_id=employees" \
    --data-urlencode "display_name=Admin API Example Config" \
    -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/admin/api/v1/create"
```

## Destroy

| Parameter      | Required | Value(s)                                                                         |
| -------------- | -------- | -------------------------------------------------------------------------------- |
| `user_id`      | Yes      | The user for which to create the configuration                                   |

**TODO**: SHOULD we also require `profile_id` to only delete config of certain 
profile?

### Request

```bash
$ curl \
    -d "user_id=foo" \
    -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/admin/api/v1/destroy"
```

# VPN Client

We'll describe how to configure VPN clients with these configuration files. 

## Windows

Complete documentation on how to setup Windows with WireGuard to have VPN 
enabled before user authentication can be found 
[here](https://github.com/WireGuard/wireguard-windows/blob/master/docs/enterprise.md).

You can deploy the configuration file and MSI through AD/GPO and enable the 
service as documented.

## macOS

Probably using 
[this](https://github.com/WireGuard/wireguard-apple/blob/master/MOBILECONFIG.md).
