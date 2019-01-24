%global git a645933e9e7b6556cfc7976aac11bb700bbeefea

Name:       vpn-user-portal
Version:    2.0.0
Release:    0.27%{?dist}
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
#        "fkooman/oauth2-server": "^3",
#        "fkooman/secookie": "^2",
#        "fkooman/sqlite-migrate": "^0",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "fkooman/php-saml-sp": "dev-master",
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
BuildRequires:  php-composer(fkooman/oauth2-server)
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(fkooman/sqlite-migrate)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(fkooman/saml-sp)
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

Requires:   roboto-fontface-fonts
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
#        "fkooman/oauth2-server": "^3",
#        "fkooman/secookie": "^2",
#        "fkooman/sqlite-migrate": "^0",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "fkooman/php-saml-sp": "dev-master",
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
Requires:   php-composer(fkooman/oauth2-server)
Requires:   php-composer(fkooman/secookie)
Requires:   php-composer(fkooman/sqlite-migrate)
Requires:   php-composer(paragonie/constant_time_encoding)
Requires:   php-composer(fkooman/saml-sp)
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
require_once '%{_datadir}/php/LetsConnect/Common/autoload.php';
require_once '%{_datadir}/php/fkooman/OAuth/Server/autoload.php';
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/fkooman/SqliteMigrate/autoload.php';
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
require_once '%{_datadir}/php/fkooman/SAML/SP/autoload.php';
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once sprintf('%s/sodium_compat.php', __DIR__);
require_once '%{_datadir}/php/random_compat/autoload.php';
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal
mkdir -p %{buildroot}%{_datadir}/php/LetsConnect/Portal
cp -pr src/* %{buildroot}%{_datadir}/php/LetsConnect/Portal

for i in add-user foreign-key-list-fetcher init
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_bindir}/vpn-user-portal-${i}
    sed -i '1s/^/#!\/usr\/bin\/env php\n/' %{buildroot}%{_bindir}/vpn-user-portal-${i}
done

cp -pr schema web views locale %{buildroot}%{_datadir}/vpn-user-portal

mkdir -p %{buildroot}%{_sysconfdir}/vpn-user-portal
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/vpn-user-portal/config.php
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
%dir %{_datadir}/php/LetsConnect
%{_datadir}/php/LetsConnect/Portal
%dir %{_datadir}/vpn-user-portal
%{_datadir}/vpn-user-portal/data
%{_datadir}/vpn-user-portal/web
%{_datadir}/vpn-user-portal/schema
%{_datadir}/vpn-user-portal/views
%{_datadir}/vpn-user-portal/config
%{_datadir}/vpn-user-portal/locale
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/vpn-user-portal
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE LICENSE.spdx

%changelog
* Wed Jan 23 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.27
- rebuilt

* Wed Jan 23 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.26
- rebuilt

* Wed Jan 23 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.25
- rebuilt

* Tue Jan 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.24
- rebuilt

* Tue Jan 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.23
- rebuilt

* Tue Jan 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.22
- rebuilt

* Tue Jan 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.21
- rebuilt

* Mon Jan 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.20
- rebuilt

* Mon Jan 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.19
- rebuilt

* Sat Jan 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.18
- rebuilt

* Thu Jan 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.17
- rebuilt

* Thu Jan 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.16
- rebuilt

* Thu Jan 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.15
- rebuilt

* Wed Jan 16 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.14
- rebuilt

* Wed Jan 16 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.13
- rebuilt

* Wed Jan 16 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.12
- rebuilt

* Wed Jan 16 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.11
- rebuilt

* Wed Jan 16 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.10
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.9
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.8
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.7
- update to 2.0.0
