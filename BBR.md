There's this new fancy 
[BBR](https://en.wikipedia.org/wiki/TCP_congestion_control#TCP_BBR) congestion 
control!

This is currently only supported on Fedora. It is also supported on Debian 10
and CentOS 8, but we do not currently support those.

To enable make sure you put the following in 
`/etc/sysctl.d/71-congestion.conf`:

    $ cat /etc/sysctl.d/71-congestion.conf 
    net.core.default_qdisc=fq
    net.ipv4.tcp_congestion_control=bbr

To enable, use `sysctl --system` or reboot.
