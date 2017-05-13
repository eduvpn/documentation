# Introduction

This document will describe how an application should work with the VPN API,
i.e. it will provide flow diagrams containing the steps that should be taken.

# Definitions

A VPN service running at a particular domain is called an _instance_, e.g. 
`demo.eduvpn.nl`. An instance can have multiple _profiles_, e.g. 
`internet` and `office`.

# Basic Flow

This assumes the user already configured the application with their favorite 
VPN instance and profile and that there are no errors.

1.  User launches app;
2.  User selects their VPN instance/profile of choice;
3.  Application performs discovery (fetches `info.json` from instance);
4.  Application fetches user info;
5.  Application fetches system and user messages using endpoints from 
    `info.json` together with the already stored OAuth access token and displays 
    them to the user;
6.  Application fetches VPN configuration for the chosen profile (using OAuth 
    access token);
7.  Application combines VPN configuration with already stored client 
    certificate and key;
8.  Application (optionally) asks for second factor;
9.  Application starts VPN with combined configuration;
10. Application shows basic VPN connection details, e.g. IP address.

Step 3 is needed as the API configuration, e.g. endpoints, can change over 
time. Step 6 is needed as the server configuration can change over time, e.g. 
new TLS cipher configuration or new VPN endpoints.

Step 4 exposes whether or not the user is enrolled for 2FA, and whether or not
the user is blocked. This information should be used by the application before
attempting to connect. If a profile requires 2FA and the user is not enrolled,
this should be indicated to the user and the enrollment process started by 
opening the browser.

# Enrollment

Adding a new instance/profile to the app consists of:

1. perform instance discovery (fetch `instances.json` and `instances.json.sig`; 
2. Verify the signature;
3. If verified document's `seq` > cached copy, update cached copy;
4. Allow the user to choose an instance, or enter their own; 
5. perform service discovery (fetch `info.json`);
6. obtaining an OAuth access token for the chosen instance;
7. obtaining a client certificate and key and store them in the persistent app 
   storage;
8. showing a list of available profiles and allowing the user to choose one, 
   e.g. `internet` or `office`.

After the enrollment the Basic Flow is executed starting at step 4.

# Configuration

Steps 6 and 7 consist of obtaining the current VPN configuration, and combining
this configuration with the client certificate and key.

Obtained configurations have everything, except the client certificate and 
private key.

The profile configuration is currently an OpenVPN configuration file, without
the `<cert>` and `<key>` fields. So to make a complete OpenVPN configuration 
file these need to be merged by adding `<cert>` and `<key>` with the values
from the client certificate and private key.

# OAuth

Many of the OAuth considerations are part of [API.md](API.md). An application
will have to deal with expiring access tokens, revoked access tokens and 
refreshing them when needed, possibly using refresh tokens if they were 
provided.

# VPN Connections

A connection to a VPN server can fail for a number of reasons, not a complete 
list:

1. The server is offline;
   * Show error to the user to try again later, or try other server from the
     configuration, but typically OpenVPN takes care of that already;
2. The VPN CA is expired;
   * If the obtained profile configuration includes the expired CA, there is 
     not much to do except show error. This needs to be resolved on the server;
3. the VPN server certificate is expired;
   * Show error, this needs to be fixed on the server;
4. The VPN client certificate is expired;
   * Obtain a new client certificate;
5. The 2FA credential is invalid or missing;
   * OpenVPN will return an authentication error in this case, ask for 2FA 
     credential again;
6. The user account is blocked;
   * OpenVPN will return an authentication error in this case, show a message;
7. The user is not, or no longer allowed to use a particular profile (ACL);
   * OpenVPN will return an authentication error in this case, give an error;

The application should deal with all this situations, deal with the issue 
automatically if possible, and if not show an appropriate error message.

**NOTE**: a blocked user will still be able to do everything using the API, 
connecting the VPN will be blocked though, this information is also exposed
through the `/user_info` call.

**NOTE**: for various situations the OpenVPN process will give the same error,
i.e. for 2FA error, blocked user or ACL issues the same "authentication error"
is returned. A profile is not listed in the `/profile_list` call if the user is
not member of the required groups (anymore) and the `/user_info` call will 
indicate whether the user is blocked. So it is possible that a `/profile_list` 
no longer shows a previously configured VPN profile because the user no longer 
has access. Appropriate errors need to be shown to the user.

# API 

More details on the API can be found in the separate 
[API documentation](API.md).

# Future

This section contains a list of changes in the future that should already be 
contemplated, although not necessarily implemented, not all is implemented at
this time in the API.

It will be required for an app to store the client certificate and key in a 
"protected" storage on the device, e.g. a secure element or otherwise tamper 
proof storage.

The application can (and must) generate their own key and have it signed by 
the API, this way the private key never leaves the device the app is running 
on.

The profile configuration will no longer consist of a "full" OpenVPN 
configuration file, but instead only contain the bare minimum in changes from 
what is the default as key/value pairs. For example, in OpenVPN >= 2.4 the 
cipher configuration is done much more automatic and does not need to be 
provided anymore.
