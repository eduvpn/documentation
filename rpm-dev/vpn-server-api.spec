%global git 3d4fc387bd00704860639cf952b52794c280086f

Name:       vpn-server-api
Version:    1.4.10
Release:    0.7%{?dist}
Summary:    Web service to control OpenVPN processes
Group:      Applications/Internet
License:    AGPLv3+
URL:        https://github.com/eduvpn/vpn-server-api
%if %{defined git}
Source0:    https://github.com/eduvpn/vpn-server-api/archive/%{git}/vpn-server-api-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/vpn-server-api/releases/download/%{version}/vpn-server-api-%{version}.tar.xz
Source1:    https://github.com/eduvpn/vpn-server-api/releases/download/%{version}/vpn-server-api-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif
Source3:    vpn-server-api-httpd.conf
Source4:    vpn-server-api.cron
Patch0:     vpn-server-api-autoload.patch

BuildArch:  noarch

BuildRequires:  gnupg2
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
#    "require-dev": {
#        "paragonie/constant_time_encoding": "^1|^2",
#        "phpunit/phpunit": "^4.8.35|^5|^6|^7"
#    },
BuildRequires:  php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  phpunit7
%global phpunit %{_bindir}/phpunit7
%else
BuildRequires:  phpunit
%global phpunit %{_bindir}/phpunit
%endif
#    "require": {
#        "LC/openvpn-connection-manager": "^1",
#        "eduvpn/common": "^1",
#        "ext-date": "*",
#        "ext-json": "*",
#        "ext-openssl": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "fkooman/otp-verifier": "^0",
#        "fkooman/sqlite-migrate": "^0",
#        "php": ">=5.4",
#        "psr/log": "^1"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-composer(LC/openvpn-connection-manager)
BuildRequires:  vpn-lib-common
BuildRequires:  php-date
BuildRequires:  php-json
BuildRequires:  php-openssl
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  php-composer(fkooman/otp-verifier)
BuildRequires:  php-composer(fkooman/sqlite-migrate)
BuildRequires:  php-composer(psr/log)

Requires:   crontabs
Requires:   openvpn
%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif
# We have an embedded modified copy of https://github.com/OpenVPN/easy-rsa
Requires:   openssl
#    "require": {
#        "LC/openvpn-connection-manager": "^1",
#        "eduvpn/common": "^1",
#        "ext-date": "*",
#        "ext-json": "*",
#        "ext-openssl": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "fkooman/otp-verifier": "^0",
#        "fkooman/sqlite-migrate": "^0",
#        "php": ">=5.4",
#        "psr/log": "^1"
#    },
Requires:   php(language) >= 5.4.0
Requires:   php-cli
Requires:   php-composer(LC/openvpn-connection-manager)
Requires:   vpn-lib-common
Requires:   php-date
Requires:   php-json
Requires:   php-openssl
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-spl
Requires:   php-composer(fkooman/otp-verifier)
Requires:   php-composer(fkooman/sqlite-migrate)
Requires:   php-composer(psr/log)

Requires(post): /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage

%description
VPN Server API.

%prep
%if %{defined git}
%setup -qn vpn-server-api-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn vpn-server-api-%{version}
%endif
%patch0 -p1

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/LC/OpenVpn/autoload.php';
require_once '%{_datadir}/php/SURFnet/VPN/Common/autoload.php';
require_once '%{_datadir}/php/fkooman/Otp/autoload.php';
require_once '%{_datadir}/php/fkooman/SqliteMigrate/autoload.php';
require_once '%{_datadir}/php/Psr/Log/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/vpn-server-api
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Server
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Server

for i in housekeeping init show-instance-info stats status update-api-secrets update-ip
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_bindir}/vpn-server-api-${i}
done

cp -pr schema web %{buildroot}%{_datadir}/vpn-server-api
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/vpn-server-api.conf

# config
mkdir -p %{buildroot}%{_sysconfdir}/vpn-server-api/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/vpn-server-api/default/config.php
ln -s ../../../etc/vpn-server-api %{buildroot}%{_datadir}/vpn-server-api/config

# data
mkdir -p %{buildroot}%{_localstatedir}/lib/vpn-server-api
ln -s ../../../var/lib/vpn-server-api %{buildroot}%{_datadir}/vpn-server-api/data

# easy-rsa
cp -pr easy-rsa %{buildroot}%{_datadir}/vpn-server-api

# cron
mkdir -p %{buildroot}%{_sysconfdir}/cron.d
%{__install} -m 0640 -D -p %{SOURCE4} %{buildroot}%{_sysconfdir}/cron.d/vpn-server-api

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-server-api(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/vpn-server-api || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-server-api(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/vpn-server-api.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/vpn-server-api
%dir %attr(0750,root,apache) %{_sysconfdir}/vpn-server-api/default
%config(noreplace) %{_sysconfdir}/vpn-server-api/default/config.php
%config(noreplace) %{_sysconfdir}/cron.d/vpn-server-api
%{_bindir}/*
%dir %{_datadir}/vpn-server-api
%{_datadir}/vpn-server-api/web
%{_datadir}/vpn-server-api/schema
%{_datadir}/vpn-server-api/easy-rsa
%{_datadir}/vpn-server-api/config
%{_datadir}/vpn-server-api/data
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Server
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/vpn-server-api
%doc README.md composer.json config/config.php.example CHANGES.md
%license LICENSE LICENSE.spdx

%changelog
* Wed Jan 09 2019 François Kooman <fkooman@tuxed.net> - 1.4.10-0.7
- rebuilt

* Mon Dec 24 2018 François Kooman <fkooman@tuxed.net> - 1.4.10-0.6
- rebuilt

* Mon Dec 24 2018 François Kooman <fkooman@tuxed.net> - 1.4.10-0.5
- rebuilt

* Mon Dec 10 2018 François Kooman <fkooman@tuxed.net> - 1.4.10-0.4
- rebuilt

* Thu Dec 06 2018 François Kooman <fkooman@tuxed.net> - 1.4.10-0.3
- rebuilt

* Thu Dec 06 2018 François Kooman <fkooman@tuxed.net> - 1.4.10-0.2
- rebuilt

* Thu Dec 06 2018 François Kooman <fkooman@tuxed.net> - 1.4.10-0.1
- update to 1.4.10

* Wed Dec 05 2018 François Kooman <fkooman@tuxed.net> - 1.4.9-1
- update to 1.4.9

* Mon Nov 26 2018 François Kooman <fkooman@tuxed.net> - 1.4.8-1
- update to 1.4.8

* Fri Nov 23 2018 François Kooman <fkooman@tuxed.net> - 1.4.7-2
- no longer "provide" easy-rsa

* Thu Nov 22 2018 François Kooman <fkooman@tuxed.net> - 1.4.7-1
- update to 1.4.7

* Fri Nov 09 2018 François Kooman <fkooman@tuxed.net> - 1.4.6-1
- update to 1.4.6

* Wed Oct 10 2018 François Kooman <fkooman@tuxed.net> - 1.4.5-1
- update to 1.4.5

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.4.4-1
- update to 1.4.4

* Sun Sep 09 2018 François Kooman <fkooman@tuxed.net> - 1.4.3-3
- merge dev and prod spec files in one
- cleanup requirements

* Sun Sep 09 2018 François Kooman <fkooman@tuxed.net> - 1.4.3-2
- add composer.json comments to (Build)Requires
- update composer dependencies
- move some stuff around to make it consistent with other spec files

* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 1.4.3-1
- update to 1.4.3
- add psr/log dependency

* Thu Jul 26 2018 François Kooman <fkooman@tuxed.net> - 1.4.2-1
- update to 1.4.2
- use phpunit7 on supported platforms
- add fkooman/sqlite-migrate dependency

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.4.1-1
- update to 1.4.1

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.4.0-3
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.4.0-2
- use fedora phpab template for generating autoloader

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.4.0-1
- update to 1.4.0

* Mon Jul 02 2018 François Kooman <fkooman@tuxed.net> - 1.3.0-1
- update to 1.3.0

* Fri Jun 29 2018 François Kooman <fkooman@tuxed.net> - 1.2.14-2
- use release tarball instead of Git tarball
- verify GPG signature

* Wed Jun 13 2018 François Kooman <fkooman@tuxed.net> - 1.2.14-1
- update to 1.2.14

* Wed Jun 06 2018 François Kooman <fkooman@tuxed.net> - 1.2.13-1
- update to 1.2.13

* Wed Jun 06 2018 François Kooman <fkooman@tuxed.net> - 1.2.12-1
- update to 1.2.12

* Tue May 22 2018 François Kooman <fkooman@tuxed.net> - 1.2.11-1
- update to 1.2.11

* Thu May 03 2018 François Kooman <fkooman@tuxed.net> - 1.2.10-1
- update to 1.2.10

* Tue Apr 17 2018 François Kooman <fkooman@tuxed.net> - 1.2.9-1
- update to 1.2.9

* Thu Apr 12 2018 François Kooman <fkooman@tuxed.net> - 1.2.8-1
- update to 1.2.8

* Thu Apr 05 2018 François Kooman <fkooman@tuxed.net> - 1.2.7-1
- update to 1.2.7

* Thu Mar 15 2018 François Kooman <fkooman@tuxed.net> - 1.2.6-1
- update to 1.2.6

* Mon Feb 26 2018 François Kooman <fkooman@tuxed.net> - 1.2.5-1
- update to 1.2.5

* Sun Feb 25 2018 François Kooman <fkooman@tuxed.net> - 1.2.4-1
- update to 1.2.4

* Wed Jan 17 2018 François Kooman <fkooman@tuxed.net> - 1.2.3-1
- update to 1.2.3

* Thu Dec 14 2017 François Kooman <fkooman@tuxed.net> - 1.2.2-1
- update to 1.2.2

* Wed Dec 13 2017 François Kooman <fkooman@tuxed.net> - 1.2.1-1
- update to 1.2.1

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 1.2.0-2
- use phpab to generate the classloader

* Tue Nov 28 2017 François Kooman <fkooman@tuxed.net> - 1.2.0-1
- update to 1.2.0

* Fri Nov 24 2017 François Kooman <fkooman@tuxed.net> - 1.1.1-1
- update to 1.1.1

* Thu Nov 23 2017 François Kooman <fkooman@tuxed.net> - 1.1.0-1
- update to 1.1.0

* Mon Nov 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.7-1
- update to 1.0.7

* Mon Oct 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.6-1
- update to 1.0.6
- add LICENSE.spdx

* Mon Oct 23 2017 François Kooman <fkooman@tuxed.net> - 1.0.5-1
- update to 1.0.5

* Wed Oct 04 2017 François Kooman <fkooman@tuxed.net> - 1.0.4-1
- update to 1.0.4

* Tue Sep 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-1
- update to 1.0.3

* Tue Aug 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-2
- update httpd snippet

* Sun Jul 23 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Fri Jul 21 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-3
- update to 1.0.1

* Tue Jul 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- remove obsolete composer variables

* Thu Jul 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
