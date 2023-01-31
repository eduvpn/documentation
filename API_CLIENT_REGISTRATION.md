# API Clients

The OAuth client registrations for the eduVPN and Let's Connect! applications
are _hard-coded_. The full list can be found 
[here](https://git.sr.ht/~fkooman/vpn-user-portal/tree/v3/item/src/OAuth/VpnClientDb.php).

In vpn-user-portal > 3.3.0 it is possible to add your own OAuth API client 
registration.

This is done by creating a JSON file in 
`/etc/vpn-user-portal/oauth_client_db.json`. 

The format is an _array_ with _objects_. See the full example below.

# Format

The object supports the following fields / types:

| Field               | Required | Type       | Default              | Example                                |
| ------------------- | -------- | ---------- | -------------------- | -------------------------------------- |
| `client_id`         | Yes      | `string`   | _N/A_                | `my-client-id`                         |
| `redirect_uris`     | Yes      | `string[]` | _N/A_                | `["https://app.example.org/callback"]` |
| `client_secret`     | No       | `string`   | _N/A_                | `s3cr3t`                               |
| `client_name`       | No       | `string`   | value of `client_id` | `My Application`                       |
| `requires_approval` | No       | `bool`     | `true`               | `false`                                |

# Example

As an example we'll list the govVPN OAuth client registrations here. This would
be the full contents of `/etc/vpn-user-portal/oauth_client_db.json`:

```json
[
    {
        "client_id": "org.govvpn.app.windows",
        "client_name": "govVPN for Windows",
        "redirect_uris": [
            "http://127.0.0.1:{PORT}/callback",
            "http://[::1]:{PORT}/callback"
        ]
    },
    {
        "client_id": "org.govvpn.app.android",
        "client_name": "govVPN for Android",
        "redirect_uris": [
            "org.govvpn.app:/api/callback"
        ]
    },
    {
        "client_id": "org.govvpn.app.ios",
        "client_name": "govVPN for iOS",
        "redirect_uris": [
            "org.govvpn.app.ios:/api/callback"
        ]
    },
    {
        "client_id": "org.govvpn.app.macos",
        "client_name": "govVPN for macOS",
        "redirect_uris": [
            "http://127.0.0.1:{PORT}/callback",
            "http://[::1]:{PORT}/callback"
        ]
    },
    {
        "client_id": "org.govvpn.app.linux",
        "client_name": "govVPN for Linux",
        "redirect_uris": [
            "http://127.0.0.1:{PORT}/callback",
            "http://[::1]:{PORT}/callback"
        ]
    }
]
```
