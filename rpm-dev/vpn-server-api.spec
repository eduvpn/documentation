%global git 93f7f714315c41d90b17303ee6e7f458bb16c04f

Name:       vpn-server-api
Version:    2.0.0
Release:    0.9%{?dist}
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
require_once '%{_datadir}/php/LetsConnect/Common/autoload.php';
require_once '%{_datadir}/php/fkooman/Otp/autoload.php';
require_once '%{_datadir}/php/fkooman/SqliteMigrate/autoload.php';
require_once '%{_datadir}/php/Psr/Log/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/vpn-server-api
mkdir -p %{buildroot}%{_datadir}/php/LetsConnect/Server
cp -pr src/* %{buildroot}%{_datadir}/php/LetsConnect/Server

for i in housekeeping init stats status update-api-secrets update-ip
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_bindir}/vpn-server-api-${i}
    sed -i '1s/^/#!\/usr\/bin\/env php\n/' %{buildroot}%{_bindir}/vpn-server-api-${i}
done

cp -pr schema web %{buildroot}%{_datadir}/vpn-server-api
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/vpn-server-api.conf

# config
mkdir -p %{buildroot}%{_sysconfdir}/vpn-server-api
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/vpn-server-api/config.php
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
%config(noreplace) %{_sysconfdir}/vpn-server-api/config.php
%config(noreplace) %{_sysconfdir}/cron.d/vpn-server-api
%{_bindir}/*
%dir %{_datadir}/vpn-server-api
%{_datadir}/vpn-server-api/web
%{_datadir}/vpn-server-api/schema
%{_datadir}/vpn-server-api/easy-rsa
%{_datadir}/vpn-server-api/config
%{_datadir}/vpn-server-api/data
%dir %{_datadir}/php/LetsConnect
%{_datadir}/php/LetsConnect/Server
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/vpn-server-api
%doc README.md composer.json config/config.php.example CHANGES.md
%license LICENSE LICENSE.spdx

%changelog
* Mon Jan 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.9
- rebuilt

* Sun Jan 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.8
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
