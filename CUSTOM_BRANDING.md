# Introduction

This document describes how to apply your own branding (style and e.g. logo) 
for the VPN user and admin portal.

# Template Overriding

The portals use templates, located in the following folders:

    /usr/share/vpn-user-portal/views
    /usr/share/vpn-admin-portal/views

You can copy the `base.php` from these folders to 
`/etc/vpn-user-portal/default/views/base.php` and 
`/etc/vpn-admin-portal/default/views/base.php` respectively and modify them to
override the defaults. For instance by adding an extra line pointing to an 
additional CSS file.

**NOTE**: It is NOT recommended to update other templates than `base.php` as 
they MAY break future software updates. We do NOT guarantee template 
compatibility!

For example, for eduVPN we use this addition to the `base.php` file under the
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

    ul.menu li.active a, ul.menu li.active span {
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
