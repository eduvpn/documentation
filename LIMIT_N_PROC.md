# LimitNPROC

**NOTE**: for new deployments (after 2022-12-07) we do this automatically now
just like in 3.x.

By default the `systemd` unit file for `openvpn-server` only allows 10 
OpenVPN processes. If you have (many) profiles and many OpenVPN processes this
may fail to start some OpenVPN processes.

To fix this we need to override this setting by adding a systemd drop-in snippet
changing only this value. You can either create a file

    /etc/systemd/system/openvpn-server@.service.d/override.conf
    
or execute the matching systemd command spawning an editor for this file

    $ sudo systemctl edit openvpn-server@.service

In the editor, add

    [Service]
    LimitNPROC=128

Now we have to apply the changes:

    $ sudo systemctl daemon-reload
    $ sudo vpn-maint-apply-changes

This should make everything work fine (again).
