There's this new fancy 
[BBR](https://en.wikipedia.org/wiki/TCP_congestion_control#TCP_BBR) congestion 
control!

This is currently only supported on Fedora and Debian. CentOS 8 also supports 
it, but we do not yet support CentOS 8.

Create the file `/etc/sysctl.d/71-congestion.conf` and put these lines in it:

    net.core.default_qdisc=fq
    net.ipv4.tcp_congestion_control=bbr

To enable, use `sysctl --system` or reboot.

To verify it is configured properly:

    $ /sbin/sysctl net.ipv4.tcp_congestion_control
    net.ipv4.tcp_congestion_control = bbr
    $ /sbin/sysctl net.core.default_qdisc
    net.core.default_qdisc = fq
