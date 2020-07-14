---
title: HTTP Proxy
description: Redirect VPN traffic over a HTTP proxy
category: advanced
---

Today we will setup a HTTP proxy to tunnel OpenVPN client traffic over. We only
care about CentOS 7 at this stage.

## Server

Make sure you install Apache:

    $ sudo yum -y install httpd

Put the following configuration snippet in `/etc/httpd/conf.d/proxy.conf`:

    ProxyRequests On
    AllowConnect 1194

    <Proxy "*">
        Require valid-user
        AuthType Basic
        AuthBasicProvider file
        AuthUserFile "/etc/httpd/proxy-users"
        AuthName "Proxy"
    </Proxy>

Add user `foo` with password `bar` to the `proxy-users` file:

    $ htpasswd -B -b -c /etc/httpd/proxy-users foo bar

Make sure you allow Apache to connect to the network:

    $ setsebool -P httpd_can_network_connect=on

Enable and start Apache:

    $ sudo systemctl enable --now httpd

That's all!

## Client

**NOTE** this will all be over **HTTP**, so the password will be sent in 
plain text!

In your OpenVPN client configuration you can enable the `http-proxy` option. 
Make sure you only list "remotes" with the TCP protocol.

For example:

    remote vpn.tuxed.net 1194 tcp

    # ...

    http-proxy proxy.tuxed.net 80 basic

    <http-proxy-user-pass>
    foo
    bar
    </http-proxy-user-pass>

You can also use IP addresses. Currently the hostname do not work as IPv6 is 
again broken on the VM platform hosting `proxy.tuxed.net`.

Client log output when connecting using a proxy:

    Thu Jul  2 23:37:28 2020 Attempting to establish TCP connection with [AF_INET]145.100.181.81:80 [nonblock]
    Thu Jul  2 23:37:29 2020 TCP connection established with [AF_INET]145.100.181.81:80
    Thu Jul  2 23:37:29 2020 Send to HTTP proxy: 'CONNECT 116.203.195.80:1194 HTTP/1.0'
    Thu Jul  2 23:37:29 2020 Send to HTTP proxy: 'Host: 116.203.195.80'
    Thu Jul  2 23:37:29 2020 Attempting Basic Proxy-Authorization
    Thu Jul  2 23:37:30 2020 HTTP proxy returned: 'HTTP/1.0 200 Connection Established'
