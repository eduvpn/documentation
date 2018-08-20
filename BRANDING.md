This document describes how to add the Let's Connect! branding to your server
installation. By default a simple "plain" unbranded installation is performed.

You can install the artwork package using `yum` or `dnf`:

    $ sudo yum -y install vpn-portal-artwork-LC

Now you can enable the `styleName` in `/etc/vpn-user-portal/default/config.php` 
and `/etc/vpn-admin-portal/default/config.php`. Set it to `LC`.

For `vpn-admin-portal` you can also configure the color of the bar graphs on
the "Stats" page.

    'statsConfig' => [
        'barColor' => [0x11, 0x93, 0xf5], // Let's Connect Blue
    ],

After finishing the configuration, make sure you wipe the template cache:

    $ sudo rm -rf /var/lib/vpn-user-portal/default/tpl
    $ sudo rm -rf /var/lib/vpn-admin-portal/default/tpl
