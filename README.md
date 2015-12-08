# Introduction
This is the eduVPN deploy manual.

# Software Requirements
CentOS >= 7.1 is the only tested deployment platform. However, it should also 
work on Fedora >= 20 and Red Hat Enterprise >= 7.1.

# Hardware Requirements
It is highly recommended to use at least three (virtual) machines to run this.

1. the `vpn-cert-service` (CERT) machine handling the signing/configuration 
   management an revocation. The web service MUST only available to the other 
   two machines
2. the `vpn-user-portal` (PORTAL) machine handling the user interaction. It 
   MUST have access to the `vpn-cert-service` and have a password to use the 
   API
3. the `vpn-manage-portal` (MANAGE) machine handling the admin operations. It
   MUST have access to the `vpn-cert-service` (to revoke) and the VPN machine
   to terminate active connections. It MUST also have access to 
   `vpn-portal-portal` to retrieve all active configurations (per user) and 
   disable user login to the portal; 
4. the OpenVPN (VPN) machine handling the VPN connections. It does not need to 
   have a connection to `vpn-user-portal` machine, and only needs read access 
   to the `ca.crl` URL on the `vpn-cert-service` machine. It does not need a 
   password to access the API

In case many users are expected, only the VPN machine needs to be distributed, 
as that will be the place where the load will be the highest.

# Security Considerations

         | VPN range
         |
    +----+----+
    |         |
    | OpenVPN +-------------+------------------+----------------+
    |         | .10         | .20              | .30            | .40
    +----+----+         +---+---+         +----+----+      +----+----+
         |              |       |         |         |      |         |
         |              | Cert  |         | Portal  |      | Manage  |
         |              |       |         |         |      |         |
         |              +-------+         +----+----+      +----+----+
         |                                     |                |
         | Internet                            | Internet       | Internet

                         
For testing purposes of course this can be deployed on one machine. But for
production you SHOULD use four machines with sufficient security in place to 
avoid unauthorized access.

## Revoking a VPN server certificate
A potential problem is the revocation of a server in case its private key falls
into the wrong hands. In order to solve this, all clients need to become 
aware of this fact and thus need to also obtain the CRL periodically. This is 
a bit of a nightmare as the CRL needs to be downloaded regularly by all the
clients. One of the potential solutions for this is use short lived server
certificates that last e.g. one day. This is cumbersome.

# Repositories
For CentOS/Red Hat Enterprise you will need to enable 
[EPEL](https://fedoraproject.org/wiki/EPEL#How_can_I_use_these_extra_packages.3F).

On CentOS you can simply install the `epel-release` package as it is part of
the CentOS extras repository (enabled by default):

    $ sudo yum -y install epel-release

# Packages
The software is contained in these projects:

- [vpn-user-portal](https://github.com/eduVPN/vpn-user-portal)
- [vpn-cert-service](https://github.com/eduVPN/vpn-cert-service)
- [vpn-crl-fetcher](https://github.com/eduVPN/vpn-crl-fetcher)
- [vpn-manage-portal](https://github.com/eduVPN/vpn-manage-portal)

The component `vpn-user-portal` is the UI for the end user, protected by SAML 
(using `mod_mellon`). It interacts with `vpn-cert-service` using a HTTP API 
protected by basic authentication.

The `vpn-cert-service` component is responsible for all the 'low level' 
configuration handling like running the CA, generating certificates, generating 
configurations, handling revocations and maintaining the CRL.

The `vpn-crl-fetcher` is responsible for fetching the CRL from 
`vpn-cert-service` for use with OpenVPN on the VPN machine.

The `vpn-manage-portal` is responsible for managing the VPN server, users and
cconfigurations.

These components depend on the following PHP libraries that are not available
in EPEL or the base repository:

- [php-fkooman-http](https://github.com/fkooman/php-lib-http)
- [php-fkooman-ini](https://github.com/fkooman/php-lib-ini)
- [php-fkooman-json](https://github.com/fkooman/php-lib-json)
- [php-fkooman-rest](https://github.com/fkooman/php-lib-rest)
- [php-fkooman-rest-plugin-authentication](https://github.com/fkooman/php-lib-rest-plugin-authentication)
- [php-fkooman-rest-plugin-authentication-basic](https://github.com/fkooman/php-lib-rest-plugin-authentication-basic)
- [php-fkooman-rest-plugin-authentication-mellon](https://github.com/fkooman/php-lib-rest-plugin-authentication-mellon)
- [php-fkooman-tpl](https://github.com/fkooman/php-lib-tpl)
- [php-fkooman-tpl-twig](https://github.com/fkooman/php-lib-tpl-twig)

These libraries are also all available as RPMs from the COPR repository as 
well, and also available as RPM specs (see below).

# Building RPMs
You can regenerate the eduVPN RPMs (or any of its dependencies) yourself from
source using the RPM spec files.

The RPM spec files can be found here: 

- https://github.com/fkooman/php-base-specs
- https://github.com/eduVPN/specs

# Installation
For your convenience the RPMs are also available from two COPR repositories:

    https://copr.fedoraproject.org/coprs/fkooman/php-base/
    https://copr.fedoraproject.org/coprs/fkooman/vpn-management/

Install PHP:

    $ sudo yum -y install php

The first one contains the dependencies, the second one the actual eduVPN 
software. To enable them see the instructions. For CentOS 7 you will need to
manually copy the `repo` files to `/etc/yum.repos.d/` as the COPR plugin for 
`yum` is not available.

To install `vpn-cert-service`: 
    
    $ sudo yum -y install vpn-cert-service

To install `vpn-user-portal`:

    $ sudo yum -y install vpn-user-portal

You will also want to install `mod_ssl`. The `mod_auth_mellon` package is an 
(indirect) dependency of `vpn-user-portal`. 

    $ sudo yum -y install mod_ssl

Now enable `httpd` by default:

    $ sudo systemctl enable httpd

# Configuration
Both `vpn-cert-service` and `vpn-user-portal` will have a working configuration
file on installation. But you SHOULD update the configuration files in 
`/etc/vpn-user-portal` and `/etc/vpn-cert-service` to suit your environment if
needed. For example if you want to use something else than SQlite, you need to
setup your database first and modify the configuration. You may also want to
update the CA certificate fields to suit your deployment.

You then need to run the database initialization scripts, they will populate
the database:

    $ sudo -u apache vpn-cert-service-init
    $ sudo -u apache vpn-user-portal-init

Do not forget to update the passwords and Apache configuration of both 
`vpn-cert-service` (`/etc/httpd/conf.d/vpn-cert-service.conf`) and 
`vpn-user-portal` (`/etc/httpd/conf.d/vpn-user-porta.conf`). They allow only 
connections from `localhost` by default. To generate a password hash you can 
use this:

    $ vpn-cert-service-generate-password-hash mySecretPass

You can add the hash to `/etc/vpn-cert-service/config.ini` and the plain text
value to `/etc/vpn-user-portal/config.ini`.

Copy the default server and client templates to the configuration directory:

    $ sudo mkdir /etc/vpn-cert-service/views
    $ sudo cp /usr/share/vpn-cert-service/views/server.twig /etc/vpn-cert-service/views
    $ sudo cp /usr/share/vpn-cert-service/views/client.twig /etc/vpn-cert-service/views

This mostly makes sense for the client template as that is used every time a 
new client configuration is generated. The server configuration that is 
generated can also easily be modified on the server, but in case you want to
deploy more servers it may make sense to already make modifications in the 
template.

# Time
CentOS 7 seems to have chrony running by default, so nothing to do here.

# SAML configuration
Using the Apache module `mod_auth_mellon`. See 
[php-fkooman-rest-plugin-authentication-mellon](https://github.com/fkooman/php-lib-rest-plugin-authentication-mellon) 
documentation for more information on how to configure `mod_auth_mellon`. There
is an example line in `/etc/httpd/conf.d/vpn-user-portal.conf` to "fake"
`mod_auth_mellon` by directly specifying the `MELLON_NAME_ID` request header.

## Example
Generate the certificate and metadata:

    $ /usr/libexec/mod_auth_mellon/mellon_create_metadata.sh https://dev.eduvpn.org/saml https://dev.eduvpn.org/saml
    Output files:
    Private key:               https_dev.eduvpn.org_saml.key
    Certificate:               https_dev.eduvpn.org_saml.cert
    Metadata:                  https_dev.eduvpn.org_saml.xml
    Host:                      dev.eduvpn.org

    Endpoints:
    SingleLogoutService:       https://dev.eduvpn.org/saml/logout
    AssertionConsumerService:  https://dev.eduvpn.org/saml/postResponse

Copy the files to the correct location:

    $ sudo mkdir /etc/httpd/saml
    $ sudo cp *.cert *.key *.xml /etc/httpd/saml/

Fetch the IdP metadata from SURFconext:

    $ curl -o SURFconext.xml https://engine.surfconext.nl/authentication/idp/metadata

Put `SURFconext.xml` in `/etc/httpd/saml` as well:

    $ sudo cp SURFconext.xml /etc/httpd/saml/

Now create a configuration in `/etc/httpd/conf.d/saml.conf`:

    # This is a server-wide configuration that will add information from the Mellon session to all requests.
    <Location />
        # Add information from the mod_auth_mellon session to the request.
        MellonEnable "info"

        # Configure the SP metadata
        # This should be the files which were created when creating SP metadata.
        MellonSPPrivateKeyFile /etc/httpd/saml/https_dev.eduvpn.org_saml.key

        MellonSPCertFile /etc/httpd/saml/https_dev.eduvpn.org_saml.cert
        MellonSPMetadataFile /etc/httpd/saml/https_dev.eduvpn.org_saml.xml

        # IdP metadata. This should be the metadata file you got from the IdP.
        MellonIdPMetadataFile /etc/httpd/saml/SURFconext.xml

        # The location all endpoints should be located under.
        # It is the URL to this location that is used as the second parameter to the metadata generation script.
        # This path is relative to the root of the web server.
        MellonEndpointPath /saml
    </Location>

    # This is a location that will trigger authentication when requested.
    <Location /vpn-user-portal>
        # This location will trigger an authentication request to the IdP.
        MellonEnable "auth"
    </Location>

Restart Apache:

    $ sudo systemctl restart httpd

Now you can access the server's metadata at the following URL:

    https://dev.eduvpn.org/saml/metadata

# Server configuration
You can now generate a OpenVPN server configuration on the `vpn-cert-service` 
machine and copy that to OpenVPN machine:

    $ sudo -u apache vpn-cert-service-generate-server-config dev.eduvpn.org

Copy/paste the output and place it in `/etc/openvpn/server.conf` on your 
OpenVPN server. Do **NOT** forget to set the permissions:

    $ sudo chmod 0600 /etc/openvpn/server.conf

To start OpenVPN and enable it on boot:

    $ sudo systemctl enable openvpn@server
    $ sudo systemctl start openvpn@server

**NOTE**: make sure to comment the line regarding the CRL as long as you don't 
have a CRL yet, otherwise OpenVPN will not start.

## NetworkManager

First we have to move the external interface to the `external` zone:

    $ nmcli connection
    NAME  UUID                                  TYPE            DEVICE 
    eth0  fe518d95-e477-4549-8786-f2844c436d91  802-3-ethernet  eth0

    $ nmcli --fields connection.zone connection show eth0
    connection.zone:                        --

Now we can modify the connection to be in the `external` zone:

    $ sudo nmcli connection modify eth0 connection.zone external

To restart NetworkManager (optional):

    $ sudo systemctl restart NetworkManager

## Firewall
I tried to get `firewalld` working, but it is not yet stable enough to do what
we need for eduVPN. For example, there is no way to configure forwarding 
without using NAT. Also IPv6 NAT is supposed to be supported, but it doesn't 
work. It is preferred to use `firewalld`, but it is not yet there. We use
`iptables` and `ip6tables` for now.

    $ sudo yum remove firewalld
    $ sudo yum -y install iptables iptables-services
    
The `/etc/sysconfig/iptables` file:

    *nat
    :PREROUTING ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING -o eth+ -j MASQUERADE
    COMMIT
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    -A INPUT -p icmp -j ACCEPT
    -A INPUT -i lo -j ACCEPT
    -A INPUT -i tun+ -j ACCEPT
    -A INPUT -m state --state NEW -m tcp -p tcp --dport 22 -j ACCEPT
    -A INPUT -m state --state NEW -m tcp -p tcp --dport 80 -j ACCEPT
    -A INPUT -m state --state NEW -m tcp -p tcp --dport 443 -j ACCEPT
    -A INPUT -m state --state NEW -m udp -p udp --dport 1194 -j ACCEPT
    -A INPUT -m state --state NEW -m tcp -p tcp --dport 8080 -j ACCEPT
    -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
    -A FORWARD -p icmp -j ACCEPT
    -A FORWARD -i lo -j ACCEPT
    -A FORWARD -i tun+ -s 10.42.42.0/24 -j ACCEPT
    -A FORWARD -i tun+ -s 10.43.43.0/24 -j ACCEPT
    -A FORWARD -o eth+ -j ACCEPT
    -A INPUT -j REJECT --reject-with icmp-host-prohibited
    -A FORWARD -j REJECT --reject-with icmp-host-prohibited
    COMMIT

The `/etc/sysconfig/ip6tables` file:

    *nat
    :PREROUTING ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING -o eth+ -j MASQUERADE
    COMMIT
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    -A INPUT -p ipv6-icmp -j ACCEPT
    -A INPUT -i lo -j ACCEPT
    -A INPUT -m state --state NEW -m udp -p udp --dport 546 -d fe80::/64 -j ACCEPT
    -A INPUT -i tun+ -j ACCEPT
    -A INPUT -m state --state NEW -m tcp -p tcp --dport 22 -j ACCEPT
    -A INPUT -m state --state NEW -m tcp -p tcp --dport 80 -j ACCEPT
    -A INPUT -m state --state NEW -m tcp -p tcp --dport 443 -j ACCEPT
    -A INPUT -m state --state NEW -m udp -p udp --dport 1194 -j ACCEPT
    -A INPUT -m state --state NEW -m tcp -p tcp --dport 8080 -j ACCEPT
    -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
    -A FORWARD -p ipv6-icmp -j ACCEPT
    -A FORWARD -i lo -j ACCEPT
    -A FORWARD -i tun+ -s fd00:4242:4242::/64 -j ACCEPT
    -A FORWARD -i tun+ -s fd00:4343:4343::/64 -j ACCEPT
    -A FORWARD -o eth+ -j ACCEPT
    -A INPUT -j REJECT --reject-with icmp6-adm-prohibited
    -A FORWARD -j REJECT --reject-with icmp6-adm-prohibited
    COMMIT
   
Now to enable them by default and start:

    $ sudo systemctl enable iptables
    $ sudo systemctl enable ip6tables
    $ sudo systemctl start iptables
    $ sudo systemctl start ip6tables

Also, enable IP forwarding by adding the following lines to `/etc/sysctl.conf`:

    net.ipv4.ip_forward = 1
    net.ipv6.conf.all.forwarding = 1

**NOTE**: there appears to be a problem with the IPv6 MTU:

    $ ping6 -M do -s 1452 -c 4 surfnet.nl
    PING surfnet.nl(2001:610:188:410:145:100:190:243) 1452 data bytes
    1460 bytes from 2001:610:188:410:145:100:190:243: icmp_seq=1 ttl=59 time=67.9 ms
    1460 bytes from 2001:610:188:410:145:100:190:243: icmp_seq=2 ttl=59 time=68.3 ms
    1460 bytes from 2001:610:188:410:145:100:190:243: icmp_seq=3 ttl=59 time=71.7 ms
    1460 bytes from 2001:610:188:410:145:100:190:243: icmp_seq=4 ttl=59 time=68.9 ms

    --- surfnet.nl ping statistics ---
    4 packets transmitted, 4 received, 0% packet loss, time 3004ms
    rtt min/avg/max/mdev = 67.934/69.252/71.727/1.508 ms
    $ ping6 -M do -s 1453 -c 4 surfnet.nl
    PING surfnet.nl(2001:610:188:410:145:100:190:243) 1453 data bytes
    ping: local error: Message too long, mtu=1500
    ping: local error: Message too long, mtu=1500
    ping: local error: Message too long, mtu=1500
    ping: local error: Message too long, mtu=1500

    --- surfnet.nl ping statistics ---
    4 packets transmitted, 0 received, +4 errors, 100% packet loss, time 2999ms

Also, it seems IPv4 is preferred by the client, at least on Fedora 22 using 
NetworkManager. This needs more investigation, also for non-NAT scenarios.

## IPv6
If you also want to enable IPv6 for use by clients the server needs to have 
an IPv6 address and a range of IPv6 addresses to give to clients. In the 
generated server configuration there are some commented lines that show you 
how to enable IPv6, just replace the IPv6 range with your range. 

The firewall example above shows the use of IPv6 NAT.

For further tweaking see the OpenVPN IPv6 
[wiki](https://community.openvpn.net/openvpn/wiki/IPv6) page. 

The following should be enough assuming the first `/64` of the IP block you 
want to use is `2001:aaaa:bbbb:cccc::`:

    server-ipv6 2001:aaaa:bbbb:cccc::/64
    push "route-ipv6 2000::/3"

You also need to modify the IPv6 firewall to allow forwarding in 
`/etc/sysconfig/ip6tables`:

    -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
    -A FORWARD -i tun0 -o eth0 -s 2001:aaaa:bbbb:cccc::/64 -j ACCEPT

## CRL
The make the CRL work, a 'cronjob' is needed to occasionally retrieve the CRL
from `vpn-cert-service`. Install `vpn-crl-fetcher` on the VPN machine:

    $ sudo yum -y install vpn-crl-fetcher

Now add a cronjob:

    $ sudo crontab -e

Put the following information there:

    */5 * * * * /usr/bin/vpn-crl-fetcher http://localhost/vpn-cert-service/api.php/ca.crl /etc/openvpn/ca.crl

Run this as often as you want. The example below makes it run every 5 minutes. 
You SHOULD use `https` and of course change the domain name to your own server.

Modify the `/etc/openvpn/server.conf` file to enable using the CRL.

    crl-verify /etc/openvpn/ca.crl

**NOTE**: if the CRL is enabled in the OpenVPN config file, but the file is 
missing or empty, OpenVPN will not work!

**NOTE**: current connections will NOT be terminated if the certificate is 
added to the CRL, only new connections will be denied.

## SELinux
Allow the management port to be used by the OpenVPN process, by default only
`udp/1194` and `tcp/1194` are allowed:

    $ sudo semanage port -l | grep openvpn_port_t

Add the management port, per instance we use one port, so if you run multiple
instances on the same host you will need multiple management ports:

    $ sudo semanage port -a -t openvpn_port_t -p tcp 7505-7508

If you also want OpenVPN te listen on TCP/443 you need to *modify* the existing
port definition, as TCP/443 already has a context, for the web server:

    $ sudo semanage port -m -t openvpn_port_t -p tcp 443

**NOTE**: you cannot run both the web server and OpenVPN on the same port, even 
though you would bind them to other IP addresses.

The end result:

    $ sudo semanage port -l | grep openvpn_port_t
    openvpn_port_t                 tcp      7505-7508, 443, 1194
    openvpn_port_t                 udp      1194

To allow Apache to execute the Easy RSA scripts, this is needed. Not sure 
what to set for PHP-FPM...

    $ sudo setsebool -P httpd_unified 1

To support updating the CRL at the OpenVPN servers, the OpenVPN instance needs
the permission to access the `ca.crl` file downloaded by the web server.

Store the below in `openvpn-allow-ca-read.te`:

    module openvpn-allow-ca-read 1.0;

    require {
	    type openvpn_t;
	    type httpd_sys_rw_content_t;
	    class dir search;
	    class file { read open };
    }

    #============= openvpn_t ==============
    allow openvpn_t httpd_sys_rw_content_t:dir search;
    allow openvpn_t httpd_sys_rw_content_t:file { read open };

This policy will allow for this. Run the following as `root`:

    # checkmodule -M -m -o openvpn-allow-ca-read.mod openvpn-allow-ca-read.te 
    # semodule_package -o openvpn-allow-ca-read.pp -m openvpn-allow-ca-read.mod 
    # semodule -i openvpn-allow-ca-read.pp

# Remote Logging
CentOS 7 uses `journald` for logging. It is super easy to forward this logging
to a remote logging service with TCP and TLS enabled.

    $ sudo yum -y install nc

The following `netcat` command can be used to send the log to the remote 
service using a `systemd` service:

    $ ncat -vvv -s 1.2.3.4 --ssl --ssl-verify \
        --ssl-trustfile /etc/pki/tls/certs/ca-bundle.crt \
        syslog.example.org 6514

You can use that command to test the connectivity. The `-s 1.2.3.4` is used
to select the source address for connecting to the log service. The host to 
connect to is `syslog.example.org` on port `6514`.

The `systemd` service file looks like this, remove the `-vvv` from the command
above:

    [Unit]
    Description=eduVPN remote logging
    After=systemd-journald.service
    Requires=systemd-journald.service

    [Service]
    ExecStart=/bin/sh -c "journalctl -u openvpn@server -f | ncat -s 1.2.3.4 --ssl --ssl-verify --ssl-trustfile /etc/pki/tls/certs/ca-bundle.crt syslog.example.org 6514"
    TimeoutStartSec=0
    Restart=on-failure
    RestartSec=5s

    [Install]
    WantedBy=multi-user.target

Copy this file to `/etc/systemd/system/eduVPN-log.service`. 

    $ sudo systemctl enable eduVPN-log
    $ sudo systemctl start eduVPN-log

This should start sending the OpenVPN logs to the remote server. If you have
multiple servers running, for example also openvpn@server-tls you have to add
that as an additional `-u openvpn@server-tls` to the `journalctl` command in
the `eduVPN-log.service` file.

# Client Management
It is possible to view the connected clients to the server as well as killing
a session.

## Showing Active Connections
It is easy to list the connected clients:

    $ telnet localhost 7505
    Trying ::1...
    telnet: connect to address ::1: Connection refused
    Trying 127.0.0.1...
    Connected to localhost.
    Escape character is '^]'.
    >INFO:OpenVPN Management Interface Version 1 -- type 'help' for more info
    status
    OpenVPN CLIENT LIST
    Updated,Tue Sep 22 09:21:42 2015
    Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since
    52a00cbd11a8d6139c36e2d4e2dc2ee89089e078_lappie,91.64.87.183:61098,12045,12540,Tue Sep 22 09:21:36 2015
    52a00cbd11a8d6139c36e2d4e2dc2ee89089e078_ug_vm,145.100.180.235:43592,12478,13064,Tue Sep 22 09:20:11 2015
    ROUTING TABLE
    Virtual Address,Common Name,Real Address,Last Ref
    fd5e:1204:b851::1001,52a00cbd11a8d6139c36e2d4e2dc2ee89089e078_ug_vm,145.100.180.235:43592,Tue Sep 22 09:20:11 2015
    10.8.0.2,52a00cbd11a8d6139c36e2d4e2dc2ee89089e078_lappie,91.64.87.183:61098,Tue Sep 22 09:21:38 2015
    fd5e:1204:b851::1000,52a00cbd11a8d6139c36e2d4e2dc2ee89089e078_lappie,91.64.87.183:61098,Tue Sep 22 09:21:38 2015
    10.8.0.3,52a00cbd11a8d6139c36e2d4e2dc2ee89089e078_ug_vm,145.100.180.235:43592,Tue Sep 22 09:20:11 2015
    GLOBAL STATS
    Max bcast/mcast queue length,0
    END

## Killing a Connection
Also, very easy to kill an existing connection:

    kill 52a00cbd11a8d6139c36e2d4e2dc2ee89089e078_ug_vm
    SUCCESS: common name '52a00cbd11a8d6139c36e2d4e2dc2ee89089e078_ug_vm' found, 1 client(s) killed

But note, that just killing a session does not prevent the client from 
reconnecting. For that to work one has to revoke the certificate first and then
kill the connection.
