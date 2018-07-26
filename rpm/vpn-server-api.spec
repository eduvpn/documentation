Name:       vpn-server-api
Version:    1.4.2
Release:    1%{?dist}
Summary:    Web service to control OpenVPN processes
Group:      Applications/Internet
License:    AGPLv3+
URL:        https://github.com/eduvpn/%{name}
Source0:    https://github.com/eduvpn/%{name}/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:    https://github.com/eduvpn/%{name}/releases/download/%{version}/%{name}-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
Source3:    %{name}-httpd.conf
Source4:    %{name}.cron
Patch0:     %{name}-autoload.patch

BuildArch:  noarch

BuildRequires:  gnupg2
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-openssl
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  php-standard
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
BuildRequires:  vpn-lib-common
BuildRequires:  php-composer(psr/log)
BuildRequires:  php-composer(fkooman/otp-verifier)
BuildRequires:  php-composer(fkooman/sqlite-migrate)
BuildRequires:  php-composer(fkooman/yubitwee)
BuildRequires:  php-composer(fkooman/oauth2-client)
BuildRequires:  php-composer(LC/openvpn-connection-manager)
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  phpunit7
%global phpunit %{_bindir}/phpunit7
%else
BuildRequires:  phpunit
%global phpunit %{_bindir}/phpunit
%endif

Requires:   crontabs
Requires:   openvpn
%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif

Requires:   php(language) >= 5.4.0
# the scripts in bin/ require the PHP CLI
Requires:   php-cli
Requires:   php-curl
Requires:   php-date
Requires:   php-json
Requires:   php-mbstring
Requires:   php-openssl
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-spl
Requires:   php-standard
Requires:   vpn-lib-common
Requires:   php-composer(psr/log)
Requires:   php-composer(fkooman/otp-verifier)
Requires:   php-composer(fkooman/sqlite-migrate)
Requires:   php-composer(fkooman/yubitwee)
Requires:   php-composer(fkooman/oauth2-client)
Requires:   php-composer(LC/openvpn-connection-manager)
Requires(post): /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage

%if 0%{?fedora} >= 24
Requires:   easy-rsa
%else
# EL7 has Easy RSA 2.x
Requires:   openssl
Provides:   bundled(easy-rsa) = 3.0.1
%endif

%description
VPN Server API.

%prep
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn %{name}-%{version}
%patch0 -p1

# remove bundled Easy RSA 3.x
%if 0%{?fedora} >= 24
rm -rf easy-rsa
%endif

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/fkooman/Otp/autoload.php';
require_once '%{_datadir}/php/fkooman/SqliteMigrate/autoload.php';
require_once '%{_datadir}/php/Psr/Log/autoload.php';
require_once '%{_datadir}/php/fkooman/YubiTwee/autoload.php';
require_once '%{_datadir}/php/fkooman/OAuth/Client/autoload.php';
require_once '%{_datadir}/php/SURFnet/VPN/Common/autoload.php';
require_once '%{_datadir}/php/LC/OpenVpn/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Server
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Server

for i in housekeeping init show-instance-info stats status update-api-secrets update-ip update
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_bindir}/vpn-server-api-${i}
done

cp -pr schema web %{buildroot}%{_datadir}/%{name}
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

# config
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/default/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

# data
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

# easy-rsa
%if 0%{?fedora} >= 24
ln -s ../../../usr/share/easy-rsa/3 %{buildroot}%{_datadir}/%{name}/easy-rsa
%else 
cp -pr easy-rsa %{buildroot}%{_datadir}/%{name}
%endif 

# cron
mkdir -p %{buildroot}%{_sysconfdir}/cron.d
%{__install} -m 0640 -D -p %{SOURCE4} %{buildroot}%{_sysconfdir}/cron.d/%{name}

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/%{name} || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}/default
%config(noreplace) %{_sysconfdir}/%{name}/default/config.php
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%{_bindir}/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/web
%{_datadir}/%{name}/schema
%{_datadir}/%{name}/easy-rsa
%{_datadir}/%{name}/config
%{_datadir}/%{name}/data
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Server
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md composer.json config/config.php.example CHANGES.md
%license LICENSE LICENSE.spdx

%changelog
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
