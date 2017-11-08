# Introduction

This document describes how to apply your own branding (style and e.g. logo) 
for the VPN user and admin portal.

# Template Overriding

The portals use templates, located in the following folders:

    /usr/share/vpn-user-portal/views
    /usr/share/vpn-admin-portal/views

You can copy the `head.twig` from these folders to 
`/etc/vpn-user-portal/default/views/head.twig` and 
`/etc/vpn-admin-portal/default/views/head.twig` respectively and modify them to
override the defaults. For instance by adding an extra line pointing to a 
second CSS file.

**NOTE**: It is NOT recommended to update other templates than `head.twig` as 
they MAY break future software updates. We do NOT guarantee template 
compatibility!

For example, for eduVPN we use this addition to the `head.twig` file under the
default CSS line:

    <link href="/css/eduvpn.css" media="screen" rel="stylesheet">

# CSS

Place, the CSS file, in this case `eduvpn.css`, and assuming your hostname is 
`vpn.example`, in `/var/www/vpn.example/css/eduvpn.css`.

For eduVPN we show a logo that is placed in 
`/var/www/vpn.example/img/eduvpn.png` that is linked to from the CSS file, 
for example:

    /** 
     * eduvpn custom style
     */
    h1, h2, h3, h4 {
        font-weight: 500;
    }

    a {
        color: #df7f0c;
    }

    ul.menu {
        /* same height as background image of the h1 */
        height: 119px;
    }

    ul.menu li.active a {
        background-color: #df7f0c;
    }

    /* only show the logo when width is >= 800px */
    @media (min-width: 800px) {
        h1 {
            display: block;
            float: right;
            color: transparent; /* hide header text */
            width: 300px;
            height: 119px;
            background-image: url("../img/eduvpn.png");
            background-repeat: no-repeat;
            background-position: 100% 0%;
        }
    }

# Cache

When you update the templates, i.e. override them like shown above, you need 
to flush the template cache:

    $ sudo rm -rf /var/lib/vpn-user-portal/default/tpl
    $ sudo rm -rf /var/lib/vpn-admin-portal/default/tpl
