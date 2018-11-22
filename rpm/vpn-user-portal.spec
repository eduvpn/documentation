#global git 8ec61da8d88eac6cc0906565d5a3e77b9214a94b

Name:       vpn-user-portal
Version:    1.8.4
Release:    1%{?dist}
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
BuildRequires:  %{_bindir}/phpab
#    "require-dev": {
#        "phpunit/phpunit": "^4.8.35|^5|^6|^7"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  phpunit7
%global phpunit %{_bindir}/phpunit7
%else
BuildRequires:  phpunit
%global phpunit %{_bindir}/phpunit
%endif
#    "require": {
#        "bacon/bacon-qr-code": "^1.0",
#        "eduvpn/common": "^1",
#        "ext-date": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "fkooman/oauth2-client": "^7",
#        "fkooman/oauth2-server": "^3",
#        "fkooman/secookie": "^2",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "php": ">=5.4.0"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-composer(bacon/bacon-qr-code)
BuildRequires:  vpn-lib-common
BuildRequires:  php-date
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  php-composer(fkooman/oauth2-client)
BuildRequires:  php-composer(fkooman/oauth2-server)
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
BuildRequires:  php-composer(paragonie/random_compat)
%endif
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  php-sodium
%else
BuildRequires:  php-pecl(libsodium)
%endif

%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif
Requires:   crontabs
#    "require": {
#        "bacon/bacon-qr-code": "^1.0",
#        "eduvpn/common": "^1",
#        "ext-date": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "fkooman/oauth2-client": "^7",
#        "fkooman/oauth2-server": "^3",
#        "fkooman/secookie": "^2",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "php": ">=5.4.0"
#    },
Requires:   php(language) >= 5.4.0
Requires:   php-cli
Requires:   php-composer(bacon/bacon-qr-code)
Requires:   vpn-lib-common
Requires:   php-date
Requires:   php-json
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-spl
Requires:   php-composer(fkooman/oauth2-client)
Requires:   php-composer(fkooman/oauth2-server)
Requires:   php-composer(fkooman/secookie)
Requires:   php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
Requires:   php-composer(paragonie/random_compat)
%endif
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
Requires:   php-sodium
%else
Requires:   php-pecl(libsodium)
%endif

Requires(post): /usr/sbin/semanage
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
require_once '%{_datadir}/php/SURFnet/VPN/Common/autoload.php';
require_once '%{_datadir}/php/fkooman/OAuth/Client/autoload.php';
require_once '%{_datadir}/php/fkooman/OAuth/Server/autoload.php';
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once sprintf('%s/sodium_compat.php', __DIR__);
require_once '%{_datadir}/php/random_compat/autoload.php';
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Portal
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Portal

for i in add-user foreign-key-list-fetcher init show-public-key generate-voucher
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_bindir}/vpn-user-portal-${i}
done

cp -pr web views locale %{buildroot}%{_datadir}/vpn-user-portal

mkdir -p %{buildroot}%{_sysconfdir}/vpn-user-portal/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/vpn-user-portal/default/config.php
ln -s ../../../etc/vpn-user-portal %{buildroot}%{_datadir}/vpn-user-portal/config

mkdir -p %{buildroot}%{_localstatedir}/lib/vpn-user-portal
ln -s ../../../var/lib/vpn-user-portal %{buildroot}%{_datadir}/vpn-user-portal/data

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

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-user-portal(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/vpn-user-portal || :

# remove template cache if it is there
rm -rf %{_localstatedir}/lib/vpn-user-portal/*/tpl/* >/dev/null 2>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-user-portal(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/vpn-user-portal.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/vpn-user-portal
%dir %attr(0750,root,apache) %{_sysconfdir}/vpn-user-portal/default
%config(noreplace) %{_sysconfdir}/vpn-user-portal/default/config.php
%config(noreplace) %{_sysconfdir}/cron.d/vpn-user-portal
%{_bindir}/*
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Portal
%dir %{_datadir}/vpn-user-portal
%{_datadir}/vpn-user-portal/data
%{_datadir}/vpn-user-portal/web
%{_datadir}/vpn-user-portal/views
%{_datadir}/vpn-user-portal/config
%{_datadir}/vpn-user-portal/locale
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/vpn-user-portal
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE LICENSE.spdx

%changelog
* Thu Nov 22 2018 François Kooman <fkooman@tuxed.net> - 1.8.4-1
- update to 1.8.4

* Mon Oct 15 2018 François Kooman <fkooman@tuxed.net> - 1.8.3-1
- update to 1.8.3

* Wed Oct 10 2018 François Kooman <fkooman@tuxed.net> - 1.8.2-1
- update to 1.8.2

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.8.1-1
- update to 1.8.1

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.8.0-2
- merge dev and prod spec files in one
- cleanup requirements

* Wed Aug 15 2018 François Kooman <fkooman@tuxed.net> - 1.8.0-1
- update to 1.8.0

* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 1.7.2-1
- update to 1.7.2
- use PHPUnit 7 on supported platforms

* Tue Jul 24 2018 François Kooman <fkooman@tuxed.net> - 1.7.1-1
- update to 1.7.1

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.7.0-3
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.7.0-2
- use fedora phpab template for generating autoloader

* Mon Jul 02 2018 François Kooman <fkooman@tuxed.net> - 1.7.0-1
- update to 1.7.0

* Fri Jun 29 2018 François Kooman <fkooman@tuxed.net> - 1.6.10-2
- use release tarball instead of Git tarball
- verify GPG signature

* Wed Jun 06 2018 François Kooman <fkooman@tuxed.net> - 1.6.10-1
- update to 1.6.10

* Thu May 24 2018 François Kooman <fkooman@tuxed.net> - 1.6.9-1
- update to 1.6.9

* Tue May 22 2018 François Kooman <fkooman@tuxed.net> - 1.6.8-1
- update to 1.6.8

* Thu May 17 2018 François Kooman <fkooman@tuxed.net> - 1.6.7-1
- update to 1.6.7

* Wed May 16 2018 François Kooman <fkooman@tuxed.net> - 1.6.6-1
- update to 1.6.6

* Thu May 10 2018 François Kooman <fkooman@tuxed.net> - 1.6.5-1
- update to 1.6.5

* Thu May 03 2018 François Kooman <fkooman@tuxed.net> - 1.6.4-1
- update to 1.6.4

* Fri Apr 20 2018 François Kooman <fkooman@tuxed.net> - 1.6.3-1
- update to 1.6.3

* Thu Apr 19 2018 François Kooman <fkooman@tuxed.net> - 1.6.2-2
- depend on php-pecl(libsodium)

* Thu Apr 12 2018 François Kooman <fkooman@tuxed.net> - 1.6.2-1
- update to 1.6.2

* Thu Mar 29 2018 François Kooman <fkooman@tuxed.net> - 1.6.1-1
- update to 1.6.1

* Mon Mar 19 2018 François Kooman <fkooman@tuxed.net> - 1.6.0-1
- update to 1.6.0

* Fri Mar 16 2018 François Kooman <fkooman@tuxed.net> - 1.5.4-1
- update to 1.5.4

* Thu Mar 15 2018 François Kooman <fkooman@tuxed.net> - 1.5.3-1
- update to 1.5.3

* Wed Feb 28 2018 François Kooman <fkooman@tuxed.net> - 1.5.2-1
- update to 1.5.2

* Mon Feb 26 2018 François Kooman <fkooman@tuxed.net> - 1.5.1-1
- update to 1.5.1
- install generate-voucher script as well

* Sun Feb 25 2018 François Kooman <fkooman@tuxed.net> - 1.5.0-1
- update to 1.5.0

* Tue Feb 06 2018 François Kooman <fkooman@tuxed.net> - 1.4.9-1
- update to 1.4.9

* Wed Jan 24 2018 François Kooman <fkooman@tuxed.net> - 1.4.8-1
- update to 1.4.8

* Mon Jan 22 2018 François Kooman <fkooman@tuxed.net> - 1.4.7-1
- update to 1.4.7

* Wed Jan 10 2018 François Kooman <fkooman@tuxed.net> - 1.4.6-1
- update to 1.4.6

* Thu Dec 28 2017 François Kooman <fkooman@tuxed.net> - 1.4.5-1
- update to 1.4.5

* Sat Dec 23 2017 François Kooman <fkooman@tuxed.net> - 1.4.4-1
- update to 1.4.4

* Thu Dec 14 2017 François Kooman <fkooman@tuxed.net> - 1.4.3-1
- update to 1.4.3

* Tue Dec 12 2017 François Kooman <fkooman@tuxed.net> - 1.4.2-1
- cleanup autoloader
- update to 1.4.2

* Fri Dec 08 2017 François Kooman <fkooman@tuxed.net> - 1.4.1-1
- update to 1.4.1
- use phpab to generate the classloader

* Tue Dec 05 2017 François Kooman <fkooman@tuxed.net> - 1.4.0-1
- update to 1.4.0

* Thu Nov 30 2017 François Kooman <fkooman@tuxed.net> - 1.3.2-1
- update to 1.3.2

* Wed Nov 29 2017 François Kooman <fkooman@tuxed.net> - 1.3.1-1
- update to 1.3.1

* Tue Nov 28 2017 François Kooman <fkooman@tuxed.net> - 1.3.0-1
- update to 1.3.0

* Thu Nov 23 2017 François Kooman <fkooman@tuxed.net> - 1.2.0-1
- update to 1.2.0

* Mon Nov 20 2017 François Kooman <fkooman@tuxed.net> - 1.1.1-1
- update to 1.1.1

* Tue Nov 14 2017 François Kooman <fkooman@tuxed.net> - 1.1.0-1
- update to 1.1.0

* Mon Nov 06 2017 François Kooman <fkooman@tuxed.net> - 1.0.10-1
- update to 1.0.10

* Thu Oct 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.9-1
- add paragonie/random_compat dependency
- update to 1.0.9
- pick the right sodium depending on OS
- cleanup web and bin script installation (using symlinks)
- add LICENSE.spdx

* Tue Oct 24 2017 François Kooman <fkooman@tuxed.net> - 1.0.8-1
- update to 1.0.8

* Tue Oct 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.7-1
- update to 1.0.7

* Mon Sep 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.6-1
- update to 1.0.6

* Thu Sep 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.5-1
- update to 1.0.5

* Mon Sep 11 2017 François Kooman <fkooman@tuxed.net> - 1.0.4-1
- update to 1.0.4

* Mon Sep 11 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-1
- update to 1.0.3

* Sun Sep 10 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Thu Aug 24 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Tue Aug 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-3
- update httpd snippet

* Tue Jul 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- remove obsolete composer variables

* Thu Jul 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
