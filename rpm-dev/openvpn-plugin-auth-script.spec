#global git fb1578c58ee158a5800efc5e5aae47e951c0517c

Name:           openvpn-plugin-auth-script
Version:        0.1.0 
Release:        1%{?dist}
Summary:        OpenVPN plugin to auth connections using non-blocking external script

License:        ASL 2.0
URL:            https://github.com/fkooman/auth-script-openvpn
%if %{defined git}
Source0:        https://github.com/fkooman/auth-script-openvpn/archive/%{git}/auth-script-openvpn-%{version}-%{git}.tar.gz
%else
Source0:        https://github.com/fkooman/auth-script-openvpn/releases/download/%{version}/auth-script-openvpn-%{version}.tar.xz
Source1:        https://github.com/fkooman/auth-script-openvpn/releases/download/%{version}/auth-script-openvpn-%{version}.tar.xz.asc
Source2:        gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif

BuildRequires:  meson
BuildRequires:  openvpn-devel
Requires:       openvpn

%description
Runs an external script to decide whether to authenticate a user or not. 
Useful for checking 2FA on VPN auth attempts as it doesn't block the main 
openvpn process, unlike passing the script to --auth-user-pass-verify flag.

The idea of the plugin is to do as little as possible, and let the external 
binary do all the heavy lifting itself.

%prep
%if %{defined git}
%setup -qn auth-script-openvpn-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn auth-script-openvpn-%{version}
%endif

%build
%meson
%meson_build

%install
mkdir -p %{buildroot}%{_libdir}/openvpn/plugins
cp -p %{_vpath_builddir}/openvpn-plugin-auth-script.so %{buildroot}%{_libdir}/openvpn/plugins

%files
%license LICENSE
%doc README.md
%{_libdir}/openvpn/plugins

%changelog
* Fri Sep 14 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-1
- update to 0.1.0

* Wed Apr 04 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.4
- update to new version to pick up new meson.build

* Wed Apr 04 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.3
- use Meson
- plugin is now called "openvpn-plugin-auth-script.so"

* Fri Oct 20 2017 François Kooman <fkooman@tuxed.net> - 0.0.0-0.2
- rebuilt

* Tue Sep 19 2017 François Kooman <fkooman@tuxed.net> - 0.0.0-0.1
- initial package
