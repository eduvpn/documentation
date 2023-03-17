# Architecture

This is a very short overview of the server architecture for version 1.0 of 
eduVPN.

## Components

The VPN service consists of the following components:

- Server API (vpn-server-api);
- Portal (vpn-user-portal);
- Server Node (vpn-server-node);

### Server API

This is the central component. It manages the CA, users, and interfaces with 
various other components, for example to verify [2FA](2FA.md) tokens or group 
[ACLs](ACL.md).

### Portal

This components is for interacting with the user through the browser. It allows
the user to download OpenVPN configuration files and enroll for 2FA. It also 
allows administrators to manage the service.

#### API

The portal has an [API](API.md) that is used by (mobile) applications to use 
the VPN service as user friendly as possible. This API implements OAuth 2.0 and 
is called the "Public API".

### Server Node

This component is used to generate OpenVPN server configurations.

## IPC

The portal, and server node components communicate with the 
server API over HTTP. They use HTTP Basic credentials for authentication. 
This is the "Private API". When the server node component is installed on 
another machine, HTTPS is used to communicate with the server API.

In addition, the server API needs to talk to the OpenVPN processes using a 
private (V)LAN, this is to kill active connections and obtain a list of 
currently connected clients.

## Authentication

The users and administrators authenticate to the portal, either with:

- username and password;
- SAML (identity federations).

The same mechanism is also used for the authentication phase of the OAuth 
authorization for the API.

## Deployment

The are two ways to deploy the software:

- run it on 1 machine (VM);
- run it on multiple machines (VMs).

When run on 1 machine, all four mentioned components are installed on the same
machine. When run on multiple machines, the portal and server API are installed 
on 1 machine, and the server node on the other machine(s).

![Architecture](img/ARCH.png)
