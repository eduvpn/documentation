This document describes how to add the Let's Connect! branding to your server
installation.

You can install the artwork package using `yum` or `dnf`:

    $ sudo yum -y install vpn-portal-artwork-LC

Now you can enable the `styleName` in `/etc/vpn-user-portal/default/config.php` 
and `/etc/vpn-admin-portal/default/config.php`. Set it to `LC`.

For `vpn-admin-portal` you can also configure the color of the bar graphs on
the "Stats" page. Uncomment one of them:

    'statsConfig' => [
        // override the color of the bars in the statistics graphs
        //'barColor' => [0x55, 0x55, 0x55], // default (gray)
        //'barColor' => [0x11, 0x93, 0xf5], // Let's Connect Blue
        //'barColor' => [0xdf, 0x7f, 0x0c], // eduVPN orange
    ],

After finishing the configuration, make sure you wipe the template cache:

    $ sudo rm -rf /var/lib/vpn-user-portal/default/tpl
    $ sudo rm -rf /var/lib/vpn-admin-portal/default/tpl
