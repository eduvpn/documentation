# Monitoring

**NOTE**: this applies only for vpn-server-api >= 2.1.3.

We have very minimal monitoring capability in the VPN software as of now. This 
will most likely be improved in the future if there is a need for it.

## Status

We have a command you can use to query the current usage of the VPN server. It
will show you the profile identifiers, the number of connected clients, the 
maximum number of clients that can connect given the existing IP space 
available for clients and the percentage of that space that is currently being 
used.

    $ sudo vpn-server-api-status 
    internet,1,10,10%
    institute,0,10,0%
    internet-utrecht,0,122,0%
    dns-only,0,122,0%

**NOTE** this format is NOT stable and SHOULD NOT be relied on for further 
scripting!

There is a special `--alert` flag that only shows lines where the percentage
of IP space being used is above 90%. You can use that from `cron` to send out
alerts when the IP space is about to be depleted.

    MAILTO=admin@example.org
    */5 * * * * /usr/bin/vpn-server-api-status --alert

Assuming `cron` is able to mail reports this should work!
