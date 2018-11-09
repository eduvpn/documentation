%global git bef1d53a0ccb68c55b06b0fd94fe87515b5c46dd

Name:       vpn-server-node
Version:    1.1.2
Release:    1%{?dist}
Summary:    OpenVPN node controller
Group:      Applications/Internet
License:    AGPLv3+
URL:        https://github.com/eduvpn/vpn-server-node
%if %{defined git}
Source0:    https://github.com/eduvpn/vpn-server-node/archive/%{git}/vpn-server-node-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/vpn-server-node/releases/download/%{version}/vpn-server-node-%{version}.tar.xz
Source1:    https://github.com/eduvpn/vpn-server-node/releases/download/%{version}/vpn-server-node-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif
Patch0:     vpn-server-node-autoload.patch

BuildArch:  noarch

BuildRequires:  gnupg2
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
#    "require-dev": {
#        "ext-json": "*",
#        "phpunit/phpunit": "^4.8.35|^5|^6|^7"
#    },
BuildRequires:  php-json
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  phpunit7
%global phpunit %{_bindir}/phpunit7
%else
BuildRequires:  phpunit
%global phpunit %{_bindir}/phpunit
%endif
#    "require": {
#        "eduvpn/common": "^1",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-mbstring": "*",
#        "ext-openssl": "*",
#        "ext-pcre": "*",
#        "ext-spl": "*",
#        "php": ">=5.4",
#        "psr/log": "^1"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  vpn-lib-common
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-mbstring
BuildRequires:  php-openssl
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  php-composer(psr/log)

Requires:   openvpn
#    "require": {
#        "eduvpn/common": "dev-master",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-mbstring": "*",
#        "ext-openssl": "*",
#        "ext-pcre": "*",
#        "ext-spl": "*",
#        "php": ">=5.4",
#        "psr/log": "^1"
#    },
Requires:   php(language) >= 5.4.0
Requires:   php-cli
Requires:   php-date
Requires:   php-filter
Requires:   php-mbstring
Requires:   php-openssl
Requires:   php-pcre
Requires:   php-spl
Requires:   php-standard
Requires:   vpn-lib-common
Requires:   php-composer(psr/log)

Requires(post): policycoreutils-python
Requires(postun): policycoreutils-python

%description
OpenVPN node controller.

%prep
%if %{defined git}
%setup -qn vpn-server-node-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn vpn-server-node-%{version}
%endif
%patch0 -p1

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/Psr/Log/autoload.php';
require_once '%{_datadir}/php/SURFnet/VPN/Common/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/vpn-server-node
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Node
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Node

# bin
for i in certificate-info generate-firewall server-config
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_bindir}/vpn-server-node-${i}
done

# libexec
for i in client-connect client-disconnect verify-otp
do
    install -m 0755 -D -p libexec/${i}.php %{buildroot}%{_libexecdir}/vpn-server-node/${i}
done

mkdir -p %{buildroot}%{_sysconfdir}/vpn-server-node/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/vpn-server-node/default/config.php
cp -pr config/firewall.php.example %{buildroot}%{_sysconfdir}/vpn-server-node/firewall.php
ln -s ../../../etc/vpn-server-node %{buildroot}%{_datadir}/vpn-server-node/config
ln -s ../../../etc/openvpn/server %{buildroot}%{_datadir}/vpn-server-node/openvpn-config

# legacy libexec symlinks
mkdir -p %{buildroot}%{_datadir}/vpn-server-node/libexec
ln -s ../../../../usr/libexec/vpn-server-node/client-connect %{buildroot}%{_datadir}/vpn-server-node/libexec/client-connect.php
ln -s ../../../../usr/libexec/vpn-server-node/client-disconnect %{buildroot}%{_datadir}/vpn-server-node/libexec/client-disconnect.php
ln -s ../../../../usr/libexec/vpn-server-node/verify-otp %{buildroot}%{_datadir}/vpn-server-node/libexec/verify-otp.php
ln -s ../../../usr/libexec/vpn-server-node/client-connect %{buildroot}%{_libexecdir}/vpn-server-node-client-connect
ln -s ../../../usr/libexec/vpn-server-node/client-disconnect %{buildroot}%{_libexecdir}/vpn-server-node-client-disconnect
ln -s ../../../usr/libexec/vpn-server-node/verify-otp %{buildroot}%{_libexecdir}/vpn-server-node-verify-otp

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%defattr(-,root,root,-)
%dir %attr(0750,root,openvpn) %{_sysconfdir}/vpn-server-node
%config(noreplace) %{_sysconfdir}/vpn-server-node/firewall.php
%dir %attr(0750,root,openvpn) %{_sysconfdir}/vpn-server-node/default
%config(noreplace) %{_sysconfdir}/vpn-server-node/default/config.php
%{_bindir}/*
%{_libexecdir}/*
%dir %{_datadir}/vpn-server-node
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Node
%{_datadir}/vpn-server-node/config
%{_datadir}/vpn-server-node/openvpn-config
# legacy libexec
%{_datadir}/vpn-server-node/libexec
%doc README.md CHANGES.md composer.json config/config.php.example config/firewall.php.example
%license LICENSE LICENSE.spdx

%changelog
* Fri Nov 09 2018 François Kooman <fkooman@tuxed.net> - 1.1.2-1
- update to 1.1.2

* Sun Oct 21 2018 François Kooman <fkooman@tuxed.net> - 1.1.1-1
- update to 1.1.1

* Mon Oct 15 2018 François Kooman <fkooman@tuxed.net> - 1.1.0-1
- update to 1.1.0

* Wed Oct 10 2018 François Kooman <fkooman@tuxed.net> - 1.0.22-1
- update to 1.0.22

* Fri Oct 05 2018 François Kooman <fkooman@tuxed.net> - 1.0.21-1
- update to 1.0.21

* Wed Sep 19 2018 François Kooman <fkooman@tuxed.net> - 1.0.20-1
- update to 1.0.20

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.0.19-1
- update to 1.0.19

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.0.18-2
- merge dev and prod spec files in one
- cleanup requirements

* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 1.0.18-1
- update to 1.0.18
- use PHPUnit 7 on supported platforms

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.0.17-3
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.0.17-2
- use fedora phpab template for generating autoloader

* Mon Jul 02 2018 François Kooman <fkooman@tuxed.net> - 1.0.17-1
- update to 1.0.17

* Fri Jun 29 2018 François Kooman <fkooman@tuxed.net> - 1.0.16-2
- use release tarball instead of Git tarball
- verify GPG signature

* Tue Jun 12 2018 François Kooman <fkooman@tuxed.net> - 1.0.16-1
- update to 1.0.16

* Wed Jun 06 2018 François Kooman <fkooman@tuxed.net> - 1.0.15-1
- update to 1.0.15

* Tue Apr 17 2018 François Kooman <fkooman@tuxed.net> - 1.0.14-1
- update to 1.0.14

* Thu Apr 12 2018 François Kooman <fkooman@tuxed.net> - 1.0.13-1
- update to 1.0.13

* Thu Apr 05 2018 François Kooman <fkooman@tuxed.net> - 1.0.12-1
- update to 1.0.12

* Thu Mar 29 2018 François Kooman <fkooman@tuxed.net> - 1.0.11-1
- update to 1.0.11

* Thu Mar 15 2018 François Kooman <fkooman@tuxed.net> - 1.0.10-1
- update to 1.0.10

* Sun Feb 25 2018 François Kooman <fkooman@tuxed.net> - 1.0.9-1
- update to 1.0.9

* Wed Jan 17 2018 François Kooman <fkooman@tuxed.net> - 1.0.8-1
- update to 1.0.8

* Sun Dec 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.7-1
- cleanup autoloading
- update to 1.0.7

* Fri Dec 15 2017 François Kooman <fkooman@tuxed.net> - 1.0.6-1
- update to 1.0.6

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.5-2
- use phpab to generate the classloader

* Mon Nov 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.5-1
- update to 1.0.5

* Wed Oct 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.4-1
- update to 1.0.4
- change handling of libexec and bin scripts by using changelogs
- add LICENSE.spdx

* Fri Oct 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-1
- update to 1.0.3

* Fri Sep 29 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Fri Jul 28 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Tue Jul 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- remove obsolete composer variables

* Thu Jul 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
