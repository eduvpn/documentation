%global git b0c6ca2f4dd354366d8e3d05ad117f067b44d773

Name:       vpn-user-portal
Version:    3.0.0
Release:    0.19%{?dist}
Summary:    VPN User Portal
Group:      Applications/Internet
License:    AGPLv3+
URL:        https://github.com/eduvpn/vpn-user-portal
%if %{defined git}
Source0:    https://github.com/eduvpn/vpn-user-portal/archive/%{git}/vpn-user-portal-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/vpn-user-portal/releases/download/%{version}/vpn-user-portal-%{version}.tar.xz
Source1:    https://github.com/eduvpn/vpn-user-portal/releases/download/%{version}/vpn-user-portal-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif
Source3:    vpn-user-portal-httpd.conf
Source4:    vpn-user-portal.cron
Patch0:     vpn-user-portal-autoload.patch

BuildArch:  noarch

BuildRequires:  gnupg2
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  phpunit8
BuildRequires:  %{_bindir}/phpab
#    "require": {
#        "bacon/bacon-qr-code": "^1.0",
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-mbstring": "*",
#        "ext-openssl": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-sodium": "*",
#        "ext-spl": "*",
#        "fkooman/jwt": "^1",
#        "fkooman/oauth2-server": "^5",
#        "fkooman/otp-verifier": "dev-master",
#        "fkooman/php-saml-sp": "^0",
#        "fkooman/secookie": "^2",
#        "fkooman/sqlite-migrate": "^0",
#        "lc/openvpn-connection-manager": "^1",
#        "paragonie/constant_time_encoding": "^2",
#        "php": ">=7.2",
#        "psr/log": "^1"
#    },
#    "require-dev": {
#        "phpunit/phpunit": "^8"
#    },
BuildRequires:  php(language) >= 7.2
BuildRequires:  php-composer(bacon/bacon-qr-code)
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-openssl
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-sodium
BuildRequires:  php-spl
BuildRequires:  php-composer(fkooman/jwt)
BuildRequires:  php-composer(fkooman/oauth2-server)
BuildRequires:  php-composer(fkooman/otp-verifier)
BuildRequires:  php-composer(fkooman/saml-sp)
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(fkooman/sqlite-migrate)
BuildRequires:  php-composer(lc/openvpn-connection-manager)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(psr/log)

Requires:   httpd-filesystem
Requires:   crontabs
#    "require": {
#        "bacon/bacon-qr-code": "^1.0",
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-mbstring": "*",
#        "ext-openssl": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-sodium": "*",
#        "ext-spl": "*",
#        "fkooman/jwt": "^1",
#        "fkooman/oauth2-server": "^5",
#        "fkooman/otp-verifier": "dev-master",
#        "fkooman/php-saml-sp": "^0",
#        "fkooman/secookie": "^2",
#        "fkooman/sqlite-migrate": "^0",
#        "lc/openvpn-connection-manager": "^1",
#        "paragonie/constant_time_encoding": "^2",
#        "php": ">=7.2",
#        "psr/log": "^1"
#    },
Requires:   php(language) >= 7.2
Requires:   php-cli
Requires:   php-composer(bacon/bacon-qr-code)
Requires:   php-date
Requires:   php-filter
Requires:   php-hash
Requires:   php-json
Requires:   php-mbstring
Requires:   php-openssl
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-sodium
Requires:   php-spl
Requires:   php-composer(fkooman/jwt)
Requires:   php-composer(fkooman/oauth2-server)
Requires:   php-composer(fkooman/otp-verifier)
Requires:   php-composer(fkooman/saml-sp)
Requires:   php-composer(fkooman/secookie)
Requires:   php-composer(fkooman/sqlite-migrate)
Requires:   php-composer(lc/openvpn-connection-manager)
Requires:   php-composer(paragonie/constant_time_encoding)
Requires:   php-composer(psr/log)
Requires(post): /usr/sbin/semanage
Requires(post): /usr/bin/openssl
Requires(postun): /usr/sbin/semanage

%description
VPN User Portal.

%prep
%if %{defined git}
%setup -qn vpn-user-portal-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn vpn-user-portal-%{version}
%endif
%patch0 -p1

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/BaconQrCode/autoload.php';
require_once '%{_datadir}/php/fkooman/Jwt/autoload.php';
require_once '%{_datadir}/php/fkooman/OAuth/Server/autoload.php';
require_once '%{_datadir}/php/fkooman/Otp/autoload.php';
require_once '%{_datadir}/php/fkooman/SAML/SP/autoload.php';
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/fkooman/SqliteMigrate/autoload.php';
require_once '%{_datadir}/php/LC/OpenVpn/autoload.php';
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
require_once '%{_datadir}/php/Psr/Log/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal
mkdir -p %{buildroot}%{_datadir}/php/LC/Portal
cp -pr src/* %{buildroot}%{_datadir}/php/LC/Portal

# bin
for i in add-user status
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_bindir}/vpn-user-portal-${i}
done

# libexec
for i in client-connect client-disconnect disconnect-expired-certificates foreign-key-list-fetcher generate-openvpn-config generate-stats housekeeping show-oauth-public-key
do
    install -m 0755 -D -p libexec/${i}.php %{buildroot}%{_libexecdir}/vpn-user-portal/${i}
done

cp -pr easy-rsa schema web views locale %{buildroot}%{_datadir}/vpn-user-portal

mkdir -p %{buildroot}%{_sysconfdir}/vpn-user-portal
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/vpn-user-portal/config.php
ln -s ../../../etc/vpn-user-portal %{buildroot}%{_datadir}/vpn-user-portal/config

mkdir -p %{buildroot}%{_localstatedir}/lib/vpn-user-portal
ln -s ../../../var/lib/vpn-user-portal %{buildroot}%{_datadir}/vpn-user-portal/data

ln -s ../../../etc/openvpn/server %{buildroot}%{_datadir}/vpn-user-portal/openvpn-config

# cron
mkdir -p %{buildroot}%{_sysconfdir}/cron.d
%{__install} -p -D -m 0640 %{SOURCE4} %{buildroot}%{_sysconfdir}/cron.d/vpn-user-portal

# httpd
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/vpn-user-portal.conf

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

/usr/bin/phpunit8 tests --verbose --bootstrap=tests/autoload.php

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-user-portal(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/vpn-user-portal || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-user-portal(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/vpn-user-portal.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/vpn-user-portal
%config(noreplace) %{_sysconfdir}/vpn-user-portal/config.php
%config(noreplace) %{_sysconfdir}/cron.d/vpn-user-portal
%{_bindir}/*
%{_libexecdir}/*
%dir %{_datadir}/php/LC
%{_datadir}/php/LC/Portal
%dir %{_datadir}/vpn-user-portal
%{_datadir}/vpn-user-portal/data
%{_datadir}/vpn-user-portal/openvpn-config
%{_datadir}/vpn-user-portal/web
%{_datadir}/vpn-user-portal/easy-rsa
%{_datadir}/vpn-user-portal/schema
%{_datadir}/vpn-user-portal/views
%{_datadir}/vpn-user-portal/config
%{_datadir}/vpn-user-portal/locale
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/vpn-user-portal
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE LICENSE.spdx

%changelog
* Thu Jun 06 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.19
- rebuilt

* Thu Jun 06 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.18
- rebuilt

* Thu Jun 06 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.17
- rebuilt

* Thu Jun 06 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.16
- rebuilt

* Thu Jun 06 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.15
- rebuilt

* Thu Jun 06 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.14
- rebuilt

* Wed Jun 05 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.13
- rebuilt

* Wed Jun 05 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.12
- rebuilt

* Wed Jun 05 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.11
- rebuilt

* Tue Jun 04 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.10
- rebuilt

* Tue Jun 04 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.9
- rebuilt

* Tue Jun 04 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.8
- rebuilt

* Tue Jun 04 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.7
- rebuilt

* Tue Jun 04 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.6
- rebuilt

* Tue Jun 04 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.5
- rebuilt

* Tue Jun 04 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.4
- rebuilt

* Tue Jun 04 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.3
- rebuilt

* Tue Jun 04 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.2
- rebuilt

* Tue Jun 04 2019 François Kooman <fkooman@tuxed.net> - 3.0.0-0.1
- update to 3.0.0

* Wed May 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.2-1
- update to 2.0.2

* Fri Apr 26 2019 François Kooman <fkooman@tuxed.net> - 2.0.1-1
- update to 2.0.1

* Mon Apr 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0
