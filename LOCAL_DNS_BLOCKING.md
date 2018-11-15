# Local DNS blocking

If you run a local DNS server on your VPN server, you can let users benefit from ad/malware/tracking domain blocking by adding a VPN profile. Additionally, this may reduce the load on your VPN server since a lot of ad content is never even requested.

Adding this feature involves a few steps. In the end, your DNS server has a special view for clients connected via the new VPN profile. This blacklist view returns `NXDOMAIN` for known bad domains, and is created and daily updated from several online sources like the [StevenBlack/hosts](https://github.com/StevenBlack/hosts) project. As an example, see the [Unbound blacklist view](https://blacklist.eduvpn.org/unbound-nxdomain.blacklist) hosted by eduVPN. 


![eduVPN DNS-blocking illustration](img/local_dns_blocking.png)



# For consideration

This DNS-blocking approach has some limitations which need to be taken into consideration first:
* Depending on your DNS server, updating the blacklist might clear the resolver's cache;
* This is a simple blacklisting approach. Ads on well-engineered websites might still show up;
* Some legitimate websites may break. Fixing these websites require a manual whitelisting action. You could also generate a blacklist composed of less restrictive sources.

# Steps to enable DNS-blocking

1. [Run your a local DNS server on your VPN server](LOCAL_DNS.md);
2. [Add an additional profile](MULTI_PROFILE.md) which will offer the blocking feature;
3. Configure the DNS server to use a special view for the new VPN profile;
4. Add and automatically renew the view.

## Run your a local DNS server on your VPN server

Follow the [instructions for setting up local DNS](LOCAL_DNS.md). The instructions in this document assume you installed Unbound. If you run another DNS resolver, then you will have to generate the blacklist view yourself ([see step 4](#other-local-dns-server)).

## Add an additional profile

Follow the [instructions](MULTI_PROFILE.md) to add the new DNS-blocking VPN profile with its own IP ranges, for example `10.158.228.0/24` and `fd05:e46c:cbb3:22f0::/60`.

## Configure the DNS server use a special view for the new VPN profile

You need to change the Unbound configuration. In the Unbound configuration file, include `.blacklist` files, and define an `access-control-view` for every IP range of the VPN profile in the `server:` clause:

    include: "/etc/unbound/unbound.conf.d/*.blacklist"
    
    ...
    
    server:
        ...
        access-control-view: 10.158.228.0/24 blacklistview
        access-control-view: fd05:e46c:cbb3:22f0::/60 blacklistview
 
In this example we refer to the view "blacklistview". In the next step we will define that view.  

## Add and automatically renew the view

### Unbound

```shell
#!/bin/sh

#
# Update Unbound blacklist
#

if test "$(id -u)" != 0
then
        echo "This script must be run as root." >&2
        exit 1
fi

BLACKLIST=unbound-nxdomain.blacklist
URL_BLACKLIST=https://blacklist.eduvpn.org/${BLACKLIST}
BLACKLIST_CHECKSUM=$(curl -s ${URL_BLACKLIST}.checksum)
PATH_LOCAL_BLACKLIST_CHECKSUM=/etc/unbound/unbound.conf.d/${BLACKLIST}.checksum

# If blacklist is downloaded before, check via the checksum if it needs to be updated
if [ -e $PATH_LOCAL_BLACKLIST_CHECKSUM ]; then
        if [ "$BLACKLIST_CHECKSUM" = "$(cat $PATH_LOCAL_BLACKLIST_CHECKSUM)" ]; then
                echo "Local blacklist is still up-to-date.";
                exit;
        fi
fi

echo "New blacklist is available.";
cd /etc/unbound/unbound.conf.d/ || exit

if [ -e $BLACKLIST ]; then
        # Create backup file of previous blacklist
        mv $BLACKLIST $BLACKLIST.bak
fi

curl -sO $URL_BLACKLIST
if unbound-control -q reload
then
        echo "Blacklist updated and Unbound reloaded."
        echo "$BLACKLIST_CHECKSUM" > $PATH_LOCAL_BLACKLIST_CHECKSUM
        # New blacklist works, remove backup
        rm $BLACKLIST.bak
else
        echo "Unbound could not reload with new blacklist."
        # Remove faulty new blacklist
        rm $BLACKLIST
        if [ -e $BLACKLIST.bak ]; then
            # Restore previous blacklist
            mv $BLACKLIST.bak $BLACKLIST
            echo "Previous blacklist restored."
    fi
fi

```

You can run the script above as superuser to add the blacklist to your Unbound installation and reload Unbound. Please note that this will also flush the cache! 
The script downloads a remote blacklistview which is updated daily. Rerun the script in your maintenance window or once a day to update the blacklist.

### Other local DNS server

Currently, eduVPN only hosts a generated blacklist view for Unbound. If you need a blacklist in the format of another DNS server, then you can [generate your own blacklist](#generating-your-own-blacklist) instead of using the blacklist hosted by eduVPN.

### Generating your own blacklist

If you prefer to generate your own blacklist, then you can run the [blacklist generator](https://github.com/shaanen/dns-blackhole) yourself. This way you can add the online sources of your liking, and add your own custom black/whitelist.
