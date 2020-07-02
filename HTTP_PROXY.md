Today we will setup a HTTP proxy to tunnel OpenVPN client traffic over. We only
care about CentOS 7 at this stage.

## Server

Make sure you install Apache:

    $ sudo yum -y install httpd

Put the following configuration snippet in `/etc/httpd/conf.d/proxy.conf`:

    ProxyRequests On
    AllowConnect 1194

    <Proxy "*">
      Require ip 145.90.228.0/23
      Require ip 2001:610:450:40::/60
    </Proxy>

The `Require ip` lines restrict access to the proxy somewhat to prevent being 
an open proxy until such time authentication is implemented properly.

Make sure you allow Apache to connect to the network:

    $ setsebool -P httpd_can_network_connect=on

Enable and start Apache:

    $ sudo systemctl enable --now httpd

That's all!

## Client

In your OpenVPN client configuration you can enable the `http-proxy` option. 
Make sure you only list "remotes" with the TCP protocol.

For example:

    remote vpn.tuxed.net 1194 tcp
    http-proxy proxy.tuxed.net 80

You can also use IP addresses. Currently the hostname do not work as IPv6 is 
again broken on the VM platform hosting proxy.tuxed.net.
