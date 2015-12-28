# OpenVPN master

Building OpenVPN master on CentOS.

# Dependencies

    $ sudo yum -y install autoconf automake gcc libtool git openssl-devel \
        lzo-devel lz4-devel pam-devel systemd-devel

# Building

    $ sudo mkdir /opt/openvpn
    $ sudo chown foo.foo /opt/openvpn    # replace foo.foo with your own userid/group
    $ git clone https://github.com/OpenVPN/openvpn.git
    $ cd openvpn
    $ autoreconf -vi
    $ ./configure --prefix=/opt/openvpn --enable-selinux --enable-systemd
    $ make
    $ make install

# Running

    $ sudo /opt/openvpn/sbin/openvpn --config /etc/openvpn/server.conf --daemon
    $ sudo /opt/openvpn/sbin/openvpn --config /etc/openvpn/server-tcp.conf --daemon

# Integration

TODO: write how to integrate this with systemd and the rest of the system, the
instructions above are only for testing!
