# Client Implementation Notes

In order to understand how to best create an implementation of an eduVPN and 
Let's Connect! client, we collected some notes that will hopefully help you 
create a better client.

This builds on the following documents:

* [API](API.md)
* [Server Discovery](SERVER_DISCOVERY.md) (eduVPN-only)

## API
This section expands upon the [API](API.md) document by giving some client-specific
implementation notes.

### Standards

As said, the server uses a simple HTTP API protected by OAuth 2, following all
recommendations of the [OAuth 2.1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/)
specification.

Please follow the OAuth specification closely, or use a library for your platform that
implements OAuth 2.1.

See section 10 of that document for a high level overview
of the changes from OAuth 2, it basically boils down:

- Only use "Authorization Code" Grant;
- Use PKCE (RFC 7636);
- Never reuse "refresh tokens";
- Only send the `Bearer` token as part of the HTTP `Authorization` Request
  Header.

For the server API you MUST use HTTPS.

### Flow
The server API was described in [API](API.md). Below we describe how the application MUST
interact with the API.
It does NOT include information on how to handle OAuth. The application MUST properly
handle OAuth, including error cases both during the authorization, when using
a "Refresh Token" and when using the API with an "Access Token".

1. Call `/info` to retrieve a list of available VPN profiles for the user;
2. Show the available profiles to the user if there is >1 profile and allow
   the user to choose. Show "No Profiles Available for your Account" when there
   are no profiles;
3. After the user chose (or there was only 1 profile) perform the `/connect`
   call as per [Connect](#connect);
4. Store the configuration file from the response. Make note of the value of
   the `Expires` response header to be able to figure out how long you are
   able to use this VPN configuration;
5. Connect to the VPN;
6. Wait for the user to request to disconnect the VPN...;
7. Disconnect the VPN;
8. Call `/disconnect`;
9. Delete the stored configuration file and its expiry time.

As long as the configuration is not "expired", according to the `Expires`
response header the same configuration SHOULD be used until the user manually
decides to disconnect. This means that during suspend, or temporary unavailable
network, the same configuration SHOULD be used. The application SHOULD
implement "online detection" to be able to figure out whether the VPN allows
any traffic over it or not.

The basic rules:

1. `/connect` (and `/disconnect`) ONLY need to be called when the user decides
   to connect/disconnect/renew, not when this happens automatically for
   whatever reason, e.g. suspending the device, network not available, ...;
2. There are no API calls as long as the VPN is (supposed to be) up (or down).

**NOTE** if the application implements some kind of "auto connect" on
(device or application) start-up that of course MUST call `/info` and
`/connect` as well! The `/info` call to be sure the profile is still available
(for the user) and the `/connect` to obtain a configuration. This does NOT
apply when the application configures a "system VPN" that also runs without the
VPN application being active. The application MUST implement a means to notify
the user when the (system VPN) configuration is about to expire.

It can of course happen that the VPN is not working when using the VPN
configuration that is not yet expired. In that case the client SHOULD inform
the user about this, e.g. through a notification that possibly opens the
application if not yet open. This allows the user to (manually)
disconnect/connect again restoring the VPN and possibly renewing the
authorization when e.g. the authorization was revoked.

### Handling error responses
The server API can have many different error responses. Do **NOT** use the exact
"Message" for string comparison in your application code. Simply checking for e.g.
4xx errors should suffice.

Errors which the client cannot handle, e.g. 5xx errors should probably be shown as a
"server error" to the user.
Possibly with a "Try Again" button. The exact error response MUST be logged and accessible by
the user if so instructed by the support desk, and MAY be shown to the user in
full, however a generic "Server Error" could be considered as well, perhaps
with a "Details..." button.

### Connecting

When getting a configuration to connect. you MUST use the `Expires` response header
value to figure out how long the VPN session will be valid for. When
implementing the client, make sure you never connect to the VPN server with an
expired VPN configuration.

To select which type of protocol to connect to, use the accept header, e.g.
`Accept: application/x-openvpn-profile` to indicate your client only supports OpenVPN.

Before using a WireGuard configuration, your locally generated private key needs to
be added under the `[Interface]` section, e.g.:

```
[Interface]
PrivateKey = AJmdZTXhNRwMT1CEvXys2T9SNYnXUG2niJVT4biXaX0=

...
```

#### Generating WireGuard keys
To generate WireGuard keypairs you MAY use [libsodium](https://doc.libsodium.org/)'s
`crypto_box_keypair()` and extract the public key using
`crypto_box_publickey()` instead of using `exec()` to run the `wg` tool.

**NOTE**: you SHOULD NOT use the same WireGuard private key for different
servers, generate one *per server*.

**NOTE**: a VPN client MAY opt to generate a new public / private key for
every new call to `/connect` instead of storing it.

### Disconnecting

The Server /disconnect API MUST ONLY be called when the _user_ decides to stop the VPN connection:

1. The user toggles the VPN connection to "off" in the application;
2. The user switches to another profile, or server;
3. The user quits the VPN application
4. The users reboots the device while the VPN is active (implicit application
   quiting)

After calling this method you MUST NOT use the same configuration again to
attempt to connect to the VPN server. First call `/info` and `/connect` again.

This call is "best effort", i.e. it is not a huge deal when the call fails. No
special care has to be taken when this call fails, e.g. the connection is dead,
or the application crashes.

This call MUST be executed *after* the VPN connection itself has been
terminated by the application, if that is possible.

When talking about "System VPNs", i.e. VPN connections that are not controlled
by the user, but by the device administrator, or possibly explicitly configured
as a "System VPN" by the user, if available, these rules do not apply.

### Expiry
The reason for discussing session expiry is that we want to avoid a user's VPN
connection terminating unexpectedly, e.g. in the middle of a video conference call.

In order to help the user avoiding unexpected VPN connection drops, the client
implements:

1. A countdown timer that shows how long the VPN session will still be valid
   for so the user is made aware of upcoming expiry;
2. A "Renew Session" button that allows the user to "refresh" the VPN session
   at a convenient time;
3. An OS notification that informs the user when the expiry is imminent, or has
   already occurred.

| What                   | Visible                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------- |
| Countdown Timer        | `${SESSION_EXPIRES_AT}` - `${NOW}` <= 24:00:00                                                      |
| "Renew Session" Button | `${SESSION_EXPIRES_AT}` - `${NOW}` <= 24:00:00 _AND_ `${NOW}` - `${SESSION_STARTED_AT}` >= 00:30:00 |
| OS Notification        | `${SESSION_EXPIRES_AT}` - `${NOW}` IN {04:00:00, 02:00:00, 01:00:00, 00:00:00}                      |

With `${NOW}` we mean the current time stamp. With `${SESSION_STARTED_AT}` we
mean the moment the OAuth authorization completed, i.e. the client obtained
their first OAuth access token. With `${SESSION_EXPIRES_AT}` we mean the time
the session expires, as obtained from the `Expires` HTTP response header
part of the `/connect` call response.

In addition to the "Countdown Timer" visible in the main application window, there is
also a timer under "Connection Info" in the UI. This timer is always visible.

When the user clicks the "Renew Session" button the following MUST happen in
this order:

1. Disconnect the active VPN connection;
2. Call `/disconnect`;
3. Delete the OAuth access and refresh token;
4. Start the OAuth authorization flow;
5. Automatically reconnect to the server and profile if (and only if) the
   client was previously connected.

The OS notification shown to the user _MAY_ offer the "Renew Session" button
inside the notification as well, if supported by the OS.

## Fail-over

The VPN client SHOULD implement support for both OpenVPN and WireGuard. OpenVPN
allows for both UDP and TCP. WireGuard only supports UDP.

Some networks block or mangle UDP connections and thus TCP is required. In the 
field we saw the following issues with UDP:

1. UDP connections are completely blocked on the network level;
2. UDP connections do not handle UDP packets of the MTU size properly.

In scenario (1) OpenVPN itself has a mechanism to fall back to TCP. It will 
try to connect using UDP, figures out that it doesn't work after a timeout and
retry with TCP. WireGuard will silently fail in this scenario.

With scenario (2) OpenVPN will also silently fail. The OpenVPN connection 
appears to be up, but it does not actually work when traffic reaches the MTU of
the connection and it will be silently dropped. A simple _ping_ over the 
connection *does* work as those packets do not get close to reaching the MTU 
size. WireGuard will also fail in this scenario as _all_ packets sent/received
by WireGuard have the exact same size.

**TODO**: is this statement about WireGuard actually true? Citation needed.

In order to resolve this situation, the client can implement a connection 
check:

1. Send a ping packet over the VPN of maximum MTU that is supposed to work;
2. Wait for the ping response to arrive.

If the ping response arrives, we know the VPN connection works!

The VPN can determine the _gateway_ in order to determine where to send a 
ping to. The gateway can be determined by calculating the first host in the
network based on the IP assigned to the VPN client. As an example, if the VPN 
client gets the IP address `10.10.10.5/24`, the IP address of the gateway is
`10.10.10.1`. If the VPN client gets the IP address `fd42::5/112` the IP 
address of the gateway is `fd42::1`.

**NOTE** you MUST implement proper gateway calculation and not simply set the 
last _octet_ to `.1` for IPv4 addresses. For example, the gateway of the 
IP address `10.10.10.130/25` is not `10.10.10.1`, but `10.10.10.129`. For IPv6
using `::1` coincidentally _does_ work in the case of eduVPN / Let's Connect! 
servers.

**NOTE** we do not implement real "online detection" as not all VPNs are used
to access the Internet, some only are used to reach resources at the 
organization and send other traffic _outside_ the VPN, i.e. "split tunnel".

The client takes the following steps:

1. Establish connection using WireGuard or OpenVPN over UDP;
2. Send a ping to the gateway;
3. Wait for the ping response (e.g. maximum 10 seconds);
4. If ping does NOT return:
    * Verify the VPN server supports OpenVPN over TCP
    * Attempt to connect over TCP

If a VPN profile does not support OpenVPN over TCP, the client can give a 
notice that the VPN connection is not working and leave it at that.

**NOTE**: the client MUST take care that the "online detection" does NOT 
interfere with OpenVPN's own fail-over mechanism, i.e. if multiple `remote` 
entries are specified of which one is TCP.
