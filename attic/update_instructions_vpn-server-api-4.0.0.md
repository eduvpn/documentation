# Update Instructions

Get a new version of the `documentation` repository, remove the existing 
copy if you have one first!

    $ rm master.tar.gz
    $ rm -rf documentation-master
    $ curl -L -O https://github.com/eduvpn/documentation/archive/master.tar.gz
    $ tar -xzf master.tar.gz

Stop the existing services:

    $ sudo systemctl stop php-fpm
    $ sudo systemctl stop sniproxy
    $ sudo systemctl stop httpd
    $ sudo systemctl stop openvpn@server-udp
    $ sudo systemctl stop openvpn@server-tcp

Update the software:

    $ sudo yum clean expire-cache && sudo yum -y update

Now update the configuration in `/etc/vpn-server-api/ip.yaml`:

If you before modified the `ip.yaml` file it will not be automatically updated,
you can now remove the `pools` section under `v4` as that is no longer 
supported. Under `v6` you need to also include the prefix size in the `prefix` 
field, so if you currently have `fd00:4242:4242:1194`, you need to update it 
to `fd00:4242:4242:1194::/60`. The network needs to be at least a `/60`, but it
can also be bigger, e.g. a `/48`.

You can also remove the `leaseDir` config field, it is no longer used.

If you are using the NAT setup you can automatically generate IP addresses for
both IPv4 and IPv6 so the change of overlap with existing network IP 
configurations is minimal:

    $ cd /path/to/documentation-master
    $ sudo php resources/update_ip.php 
    IPv4 CIDR  : 10.165.139.0/24
    IPv6 prefix: fd49:2d18:edd6::/48

After you did this, you have to regenerate the server configuration, the 
firewall and restart all the services:

The server config, it will reuse the existing keys/certificates:

    $ sudo vpn-server-api-server-config --reuse

The firewall, if you use NAT specify `--nat`, and make sure to use the correct
interface:

    $ sudo vpn-server-api-generate-firewall --nat --install eth0

Restart the firewall:

    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables

Restart the rest:

    $ sudo systemctl restart openvpn@server-udp
    $ sudo systemctl restart openvpn@server-tcp
    $ sudo systemctl restart php-fpm
    $ sudo systemctl restart httpd
    $ sudo systemctl restart sniproxy

If you installed CentOS 7 from a cloud image, it may not have the correct 
locales installed by default, you can verify this by running `locale -a` to 
see if there is a complete list, if there is only `en_XX` you may need to 
reinstall `glibc-common`:

    $ sudo yum reinstall glibc-common

That should fix it.

Now update the configuration in `/etc/vpn-user-portal/config.yaml`, the
`companionAppUrl` entry can be completely removed, it is no longer needed.

If you are using the eduvpn branding, you need to update the `footer.twig` to
allow for switching the language. Follow the instructions in the 
`eduvpn.surfcloud.nl` folder of the private eduvpn repository for installing 
the branding 

