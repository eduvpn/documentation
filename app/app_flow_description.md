# Application Flow

## Home Screen (1)

This screen lists the currently configured VPN profiles, if any.

The "Add Provider" button will try to fetch a new `instances.json`, if this 
works the _global_ cached `instances.json` is updated, if it fails we fall back
to the old version.

If the user chooses "Add Provider", move to 2.

If the user chooses "Connect" for any of the listed profiles, move to 6.

## Add Provider Screen (2)

This displays a list of VPN providers, and also a manual input option. The 
user is allowed to choose a provider here.

Move to 3.

## Discover Profiles (3)

If there is already an `info.json` of this provider in the _provider_ cache, 
use it, if it is not there, fetch it and store it in the _provider_ cache. If 
there is an error fetching the new `info.json` display error.

**NOTE**: maybe the provider was removed, and is also no longer available, but
we _just_ fetched the `instances.json`. So if this gives an error, we cannot do
anything, just display it to the user.

If there is _no_ `access_token`, obtain it and store it in the _provider_ 
cache. 

If there is an `access_token` for this provider in the _provider_ cache, use it
together with the `profile_list` endpoint to try to fetch the profile list.

If this is OK, move to (4)

If this returns a `4xx` error, delete the `info.json` and `access_token` from 
the cache and move to (3) again.

## List Profiles (4)

This lists the profiles the user has access to at this provider. Allow the 
user to choose one. 

Move to (5).

## Download Configuration (5)

Do we already have a configuration for this particular provider and profile? 

If yes move to (1). 

If no, obtain the configuration from the `create_config` endpoint from 
`info.json` together with the `access_token`. Store, it as an OpenVPN 
configuration. 

If this is OK, move to (1)

If this returns a `4xx` error, delete the `info.json` and `access_token` from 
the cache and move to (3) again.

## Connect to VPN (6)

Try to establish the connection.

If the connection is established, move to 7.

If the connection cannot be established, there could be two reasons: 

* authentication failure, maybe the user or admin has disabled the 
  configuration (or OTP is needed)
* there is any other (network) error. 

If the first, display error and allow the user to reconfigure, e.g. delete the 
configuration, or "Try again", or show info about contacting support. Move to
(1)

If the second, we can offer to try again, or advise the user to "Force TCP" in 
the settings. Move to 1.

## Connection Info (7)

Show information about the current connection.

Allow the user to disconnect, doing this moves to 1.
