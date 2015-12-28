# Windows

This document describes how to create a Windows binary from scratch and how
to customize the build and integrate a configuration file.

TODO:
- sign the build
- verify the downloaded tarballs

# Sources

- https://community.openvpn.net/openvpn/wiki/BuildingUsingGenericBuildsystem

# Dependencies

We use Fedora 23 as the OS to build the Windows installer because it has 
working cross compilers for Windows binaries.

    $ sudo dnf -y install mingw32-gcc mingw64-gcc man2html mingw32-nsiswrapper \
        mingw32-nsis osslsigncode git gcc wget unzip make unix2dos

# Build System

We use the offical OpenVPN build system available on GitHub:

    $ git clone https://github.com/OpenVPN/openvpn-build.git
    $ cd openvpn-build/windows-nsis

Update the variables to point to the latest versions of the dependencies, this
matches the dependency versions of the last official Windows release from 
`openvpn.net`:

    $ export OPENSSL_VERSION=1.0.1q
    $ export OPENVPN_VERSION=2.3.9
    $ export OPENVPN_GUI_VERSION=8 
    $ export LZO_VERSION=2.09

Now build the dependency cache:

    $ ./build-complete --build-depcache

Then you can build the system with enabling the depdency cache to speed up
building:

    $ ./build-complete --use-depcache

This will build both a i686 and x86_64 Windows installer.

# Customizing

TBD.
Now we want to add a default config file to the 
`C:\Program Files\OpenVPN\Config` folder.

TBD.
And we want to by default run as administrator...

