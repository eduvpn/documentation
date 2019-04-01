%global git 97583675de344a5bf1f4a2c899ff26768ed3cddd

Name:       vpn-user-portal
Version:    2.0.0
Release:    0.102%{?dist}
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
#        "ext-date": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "fkooman/jwt": "^1",
#        "fkooman/oauth2-server": "^5",
#        "fkooman/php-saml-sp": "^0",
#        "fkooman/secookie": "^2",
#        "fkooman/sqlite-migrate": "^0",
#        "lc/common": "dev-master",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "php": ">=5.4.0"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-composer(bacon/bacon-qr-code)
BuildRequires:  php-date
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  php-composer(fkooman/jwt)
BuildRequires:  php-composer(fkooman/oauth2-server)
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(fkooman/sqlite-migrate)
BuildRequires:  php-composer(lc/common)
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
#        "ext-date": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "fkooman/jwt": "^1",
#        "fkooman/oauth2-server": "^5",
#        "fkooman/php-saml-sp": "^0",
#        "fkooman/secookie": "^2",
#        "fkooman/sqlite-migrate": "^0",
#        "lc/common": "dev-master",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "php": ">=5.4.0"
#    },
Requires:   php(language) >= 5.4.0
Requires:   php-cli
Requires:   php-composer(bacon/bacon-qr-code)
Requires:   php-date
Requires:   php-json
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-spl
Requires:   php-composer(fkooman/jwt)
Requires:   php-composer(fkooman/oauth2-server)
Requires:   php-composer(fkooman/secookie)
Requires:   php-composer(fkooman/sqlite-migrate)
Requires:   php-composer(lc/common)
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
require_once '%{_datadir}/php/LC/Common/autoload.php';
require_once '%{_datadir}/php/fkooman/Jwt/autoload.php';
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
mkdir -p %{buildroot}%{_datadir}/php/LC/Portal
cp -pr src/* %{buildroot}%{_datadir}/php/LC/Portal

for i in add-user foreign-key-list-fetcher init generate-oauth-key show-oauth-key
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

# generate SAML keys if they do not yet exist
if [ ! -f "%{_sysconfdir}/%{name}/sp.key" ]
then
    /usr/bin/openssl \
        req \
        -nodes \
        -subj "/CN=SAML SP" \
        -x509 \
        -sha256 \
        -newkey rsa:2048 \
        -keyout "%{_sysconfdir}/%{name}/sp.key" \
        -out "%{_sysconfdir}/%{name}/sp.crt" \
        -days 1825 \
        2>/dev/null
    # allow web server to read the private key
    /usr/bin/chmod 0644 %{_sysconfdir}/%{name}/sp.key
fi

# Generate OAuth key if it not yet exists
if [ ! -f "%{_sysconfdir}/%{name}/secret.key" ]
then
    %{_bindir}/vpn-user-portal-generate-oauth-key
fi

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
%dir %{_datadir}/php/LC
%{_datadir}/php/LC/Portal
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
* Mon Apr 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.102
- rebuilt

* Mon Apr 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.101
- rebuilt

* Fri Mar 29 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.100
- rebuilt

* Thu Mar 28 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.99
- rebuilt

* Thu Mar 28 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.98
- rebuilt

* Thu Mar 28 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.97
- rebuilt

* Thu Mar 28 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.96
- rebuilt

* Wed Mar 27 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.95
- rebuilt

* Wed Mar 27 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.94
- rebuilt

* Wed Mar 27 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.93
- rebuilt

* Wed Mar 27 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.92
- rebuilt

* Wed Mar 27 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.91
- rebuilt

* Wed Mar 27 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.90
- rebuilt

* Fri Mar 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.89
- rebuilt

* Fri Mar 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.88
- rebuilt

* Fri Mar 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.87
- rebuilt

* Fri Mar 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.86
- rebuilt

* Fri Mar 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.85
- rebuilt

* Thu Mar 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.84
- rebuilt

* Thu Mar 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.83
- rebuilt

* Thu Mar 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.82
- rebuilt

* Thu Mar 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.81
- rebuilt

* Thu Mar 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.80
- rebuilt

* Wed Mar 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.79
- rebuilt

* Wed Mar 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.78
- rebuilt

* Wed Mar 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.77
- rebuilt

* Wed Mar 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.76
- rebuilt

* Wed Mar 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.75
- rebuilt

* Mon Mar 18 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.74
- rebuilt

* Fri Mar 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.73
- rebuilt

* Thu Mar 14 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.72
- rebuilt

* Wed Mar 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.71
- rebuilt

* Wed Mar 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.70
- rebuilt

* Wed Mar 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.69
- rebuilt

* Wed Mar 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.68
- rebuilt

* Wed Mar 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.67
- rebuilt

* Thu Mar 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.66
- rebuilt

* Wed Mar 06 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.65
- rebuilt

* Tue Mar 05 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.64
- rebuilt

* Tue Mar 05 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.63
- rebuilt

* Mon Mar 04 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.62
- rebuilt

* Mon Mar 04 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.61
- rebuilt

* Fri Mar 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.60
- rebuilt

* Mon Feb 25 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.59
- rebuilt

* Sun Feb 24 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.58
- rebuilt

* Tue Feb 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.57
- rebuilt

* Mon Feb 18 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.56
- rebuilt

* Fri Feb 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.55
- rebuilt

* Fri Feb 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.54
- rebuilt

* Fri Feb 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.53
- rebuilt

* Wed Feb 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.52
- rebuilt

* Wed Feb 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.51
- rebuilt

* Wed Feb 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.50
- rebuilt

* Fri Feb 08 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.49
- rebuilt

* Fri Feb 08 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.48
- rebuilt

* Thu Feb 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.47
- rebuilt

* Thu Feb 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.46
- rebuilt

* Thu Feb 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.45
- rebuilt

* Thu Feb 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.44
- rebuilt

* Thu Feb 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.43
- rebuilt

* Thu Feb 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.42
- rebuilt

* Mon Feb 04 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.41
- rebuilt

* Mon Feb 04 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.40
- rebuilt

* Mon Feb 04 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.39
- rebuilt

* Mon Feb 04 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.38
- rebuilt

* Mon Feb 04 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.37
- rebuilt

* Mon Feb 04 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.36
- rebuilt

* Fri Jan 25 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.35
- rebuilt

* Fri Jan 25 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.34
- rebuilt

* Fri Jan 25 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.33
- rebuilt

* Fri Jan 25 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.32
- rebuilt

* Fri Jan 25 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.31
- rebuilt

* Thu Jan 24 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.30
- rebuilt

* Thu Jan 24 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.29
- rebuilt

* Thu Jan 24 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.28
- rebuilt

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
