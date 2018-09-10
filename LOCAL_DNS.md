It is possible, and most likely a good idea to run a local recursive DNS server 
on your VPN server. Especially for simple deploys where you have only one VPN 
server.

**NOTE**: in the future this _may_ become the default on new deployments!

The benefit is that you don't have to use any of the public DNS servers like 
for example the ones offered by Google, Quad9 or Cloudflare.

**NOTE**: if your organization already has (trusted) DNS servers, there is no 
need to use a local DNS server, you can configure the existing DNS servers 
using the `dns` setting in `/etc/vpn-server-api/default/config.php`.

Setting a local recursive DNS server takes a few steps:

1. Install a recursive DNS server, we'll use 
   [Unbound](https://nlnetlabs.nl/projects/unbound/about/) here;
2. Configure the DNS server to allow the VPN clients to use it for recursive
   queries;
3. Configure the VPN firewall to allow VPN clients to access the local DNS 
   server.

# Install Unbound

## CentOS 

    $ sudo yum -y install unbound

## Fedora

    $ sudo dnf -y install unbound

## Debian 

    $ sudo apt-get -y install unbound

# Configuration

## Unbound

You need to change the Unbound configuration. You can add the following file
to `/etc/unbound/conf.d/VPN.conf` on CentOS/Fedora, and in 
`/etc/unbound/unbound.conf.d/VPN.conf` on Debian:

    server:
        interface: 0.0.0.0
        interface: ::0
        access-control: 10.0.0.0/8 allow
        access-control: fd00::/8 allow
 
With these options Unbound listens on all interfaces and the ranges 
`10.0.0.0/8` and `fd00::/8` are white-listed. These ranges are the defaults for 
deploys done by the `deploy_${DIST}.sh` scripts.

Enable Unbound during boot, and (re)start it:

    $ sudo systemctl enable unbound
    $ sudo systemctl restart unbound

## VPN

Modify `/etc/vpn-server-api/default/config.php` and make sure the `dns` entry
is an empty array:

    'dns' => [],

By not specifying the DNS servers here the IPv4 and IPv6 gateway addresses of 
the VPN server are pushed to the clients.

## Firewall

Modify `/etc/vpn-server-node/firewall.php` to allow traffic from the VPN
clients to both `udp/53` and `tcp/53`. Replace the IP ranges with your VPN 
client ranges:

    'inputChain' => [
        'tcp' => [
    
            ...

            // allow VPN clients to query local DNS server
            ['src' => ['10.0.0.0/8', 'fd00::/8'], 'port' => '53'],

            ...

        ],
        'udp' => [

            ...

            // allow VPN clients to query local DNS server
            ['src' => ['10.0.0.0/8', 'fd00::/8'], 'port' => '53'],

            ...

        ],
    ],

## Apply

Do not forget to [apply](PROFILE_CONFIG.md#apply-changes) the changes!
