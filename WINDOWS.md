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
        mingw32-nsis osslsigncode git gcc wget unzip make unix2dos autoconf \
        automake libtool    

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

## Run as Administrator

The `openvpn-gui.manifest` needs to be modified to request the correct 
privileges when running.

    diff --git a/generic/build b/generic/build
    index daac1ce..27edc07 100755
    --- a/generic/build
    +++ b/generic/build
    @@ -301,6 +301,8 @@ build_openvpn_gui() {
     
     	echo "Build openvpn-gui"
     	cd "${BUILDROOT}/openvpn-gui"* || die "cd openvpn gui"
    +        # update manifest to always run as administrator
    +        sed -i "s/asInvoker/requireAdministrator/" res/openvpn-gui.manifest 
     	./configure ${CONFIGOPTS} ${EXTRA_OPENVPN_GUI_CONFIG} \
     		|| die "Configure openvpn-gui"
     	${MAKE} ${MAKEOPTS} ${MAKE_AUTOCONF_INSTALL_TARGET} DESTDIR="${OPENVPN_ROOT}" || die "make openvpn-gui"

## Add a configuration file

Now we want to add a default config file to the 
`C:\Program Files\OpenVPN\Config` folder. Assuming you built the OpenVPN 
installer according to the instructions above, we can just re-run the `nsis` 
command to generate an updated installer with the configuration file 
embedded.

We first have to patch `openvpn.nsi` to actually add the configuration file 
during the installer build:

    diff --git a/windows-nsis/openvpn.nsi b/windows-nsis/openvpn.nsi
    index f25f00f..5fa679f 100755
    --- a/windows-nsis/openvpn.nsi
    +++ b/windows-nsis/openvpn.nsi
    @@ -267,6 +267,7 @@ Section /o "${PACKAGE_NAME} Service" SecService
            FileWrite $R0 "When ${PACKAGE_NAME} is started as a service, a separate ${PACKAGE_NAME}$\r$\n"
            FileWrite $R0 "process will be instantiated for each configuration file.$\r$\n"
            FileClose $R0
    +       File "${EMBED_CONFIG}"
     
            SetOutPath "$INSTDIR\sample-config"
            File "${OPENVPN_ROOT}\share\doc\openvpn\sample\sample.${OPENVPN_CONFIG_EXT}"

Now we can run `makensis`:

    $ makensis -DARCH=x86_64\
        -DEMBED_CONFIG=/path/to/config.ovpn
	    -DVERSION_STRING=2.3.9-I601\
	    -DOPENVPN_ROOT=tmp\\installer\\openvpn\
	    -DTAP_WINDOWS_INSTALLER=tmp\\tap-windows-9.21.1.exe\
	    -DSPECIAL_BUILD=eduvpn\
	    -DUSE_TAP_WINDOWS\
	    -DEASYRSA_ROOT=tmp\\installer\\easy-rsa\
	    -DUSE_EASYRSA\
	    -DUSE_OPENVPN_GUI\
	    -DOUTPUT=./openvpn-install-2.3.9-I601-x86_64-eduvpn.exe\
	    -DPACKAGE_NAME=OpenVPN openvpn.nsi

This should give you an updated installer with the configuration embedded!
