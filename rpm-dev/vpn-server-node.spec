%global git 147f97c678b8dea137605e0e91b5faf5ca507047

Name:       vpn-server-node
Version:    2.0.0
Release:    0.24%{?dist}
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
#        "lc/common": "dev-master",
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
BuildRequires:  php-composer(lc/common)
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-mbstring
BuildRequires:  php-openssl
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  php-composer(psr/log)

Requires:   openvpn
#    "require": {
#        "lc/common": "dev-master",
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
Requires:   php-composer(lc/common)
Requires:   php-cli
Requires:   php-date
Requires:   php-filter
Requires:   php-mbstring
Requires:   php-openssl
Requires:   php-pcre
Requires:   php-spl
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
require_once '%{_datadir}/php/LC/Common/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/vpn-server-node
mkdir -p %{buildroot}%{_datadir}/php/LC/Node
cp -pr src/* %{buildroot}%{_datadir}/php/LC/Node

# bin
for i in certificate-info generate-firewall server-config
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_bindir}/vpn-server-node-${i}
    sed -i '1s/^/#!\/usr\/bin\/env php\n/' %{buildroot}%{_bindir}/vpn-server-node-${i}
done

# libexec
for i in client-connect client-disconnect
do
    install -m 0755 -D -p libexec/${i}.php %{buildroot}%{_libexecdir}/vpn-server-node/${i}
    sed -i '1s/^/#!\/usr\/bin\/env php\n/' %{buildroot}%{_libexecdir}/vpn-server-node/${i}
done

mkdir -p %{buildroot}%{_sysconfdir}/vpn-server-node
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/vpn-server-node/config.php
cp -pr config/firewall.php.example %{buildroot}%{_sysconfdir}/vpn-server-node/firewall.php
ln -s ../../../etc/vpn-server-node %{buildroot}%{_datadir}/vpn-server-node/config
ln -s ../../../etc/openvpn/server %{buildroot}%{_datadir}/vpn-server-node/openvpn-config

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
%config(noreplace) %{_sysconfdir}/vpn-server-node/config.php
%{_bindir}/*
%{_libexecdir}/*
%dir %{_datadir}/vpn-server-node
%dir %{_datadir}/php/LC
%{_datadir}/php/LC/Node
%{_datadir}/vpn-server-node/config
%{_datadir}/vpn-server-node/openvpn-config
%doc README.md CHANGES.md composer.json config/config.php.example config/firewall.php.example
%license LICENSE LICENSE.spdx

%changelog
* Mon Apr 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.24
- rebuilt

* Thu Mar 14 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.23
- rebuilt

* Thu Mar 14 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.22
- rebuilt

* Thu Mar 14 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.21
- rebuilt

* Thu Feb 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.20
- rebuilt

* Thu Feb 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.19
- rebuilt

* Thu Feb 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.18
- rebuilt

* Thu Feb 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.17
- rebuilt

* Thu Feb 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.16
- rebuilt

* Mon Feb 18 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.15
- rebuilt

* Mon Feb 18 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.14
- rebuilt

* Mon Feb 18 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.13
- rebuilt

* Mon Feb 18 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.12
- rebuilt

* Mon Feb 18 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.11
- rebuilt

* Tue Feb 05 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.10
- rebuilt

* Sun Jan 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.9
- rebuilt

* Thu Jan 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.8
- rebuilt

* Thu Jan 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.7
- rebuilt

* Thu Jan 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.6
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.5
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.4
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.3
- update to 2.0.0
