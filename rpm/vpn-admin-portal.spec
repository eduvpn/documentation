#global git 063418350e91ef1f35c7b4d2fd6f5745b7d1f05f

Name:       vpn-admin-portal
Version:    1.7.3
Release:    1%{?dist}
Summary:    VPN Admin Portal
Group:      Applications/Internet
License:    AGPLv3+
URL:        https://github.com/eduvpn/vpn-admin-portal
%if %{defined git}
Source0:    https://github.com/eduvpn/vpn-admin-portal/archive/%{git}/vpn-admin-portal-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/vpn-admin-portal/releases/download/%{version}/vpn-admin-portal-%{version}.tar.xz
Source1:    https://github.com/eduvpn/vpn-admin-portal/releases/download/%{version}/vpn-admin-portal-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif
Source3:    vpn-admin-portal-httpd.conf
Patch0:     vpn-admin-portal-autoload.patch

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
#        "eduvpn/common": "dev-master",
#        "ext-date": "*",
#        "ext-gd": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "fkooman/secookie": "^2",
#        "php": ">5.4",
#        "twig/twig": "^1"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  vpn-lib-common
BuildRequires:  php-date
BuildRequires:  php-gd
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(twig/twig) < 2

Requires:   roboto-fontface-fonts
%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif
#    "require": {
#        "eduvpn/common": "dev-master",
#        "ext-date": "*",
#        "ext-gd": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "fkooman/secookie": "^2",
#        "php": ">5.4",
#        "twig/twig": "^1"
#    },
Requires:   php(language) >= 5.4.0
Requires:   php-cli
Requires:   vpn-lib-common
Requires:   php-date
Requires:   php-gd
Requires:   php-pdo
Requires:   php-spl
Requires:   php-composer(fkooman/secookie)
Requires:   php-composer(twig/twig) < 2

Requires(post): /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage

%description
VPN Admin Portal.

%prep
%if %{defined git}
%setup -qn vpn-admin-portal-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn vpn-admin-portal-%{version}
%endif
%patch0 -p1

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/SURFnet/VPN/Common/autoload.php';
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/Twig/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/vpn-admin-portal
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Admin
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Admin
install -m 0755 -D -p bin/add-user.php %{buildroot}%{_bindir}/vpn-admin-portal-add-user
cp -pr web views locale %{buildroot}%{_datadir}/vpn-admin-portal

mkdir -p %{buildroot}%{_sysconfdir}/vpn-admin-portal/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/vpn-admin-portal/default/config.php
ln -s ../../../etc/vpn-admin-portal %{buildroot}%{_datadir}/vpn-admin-portal/config

mkdir -p %{buildroot}%{_localstatedir}/lib/vpn-admin-portal
ln -s ../../../var/lib/vpn-admin-portal %{buildroot}%{_datadir}/vpn-admin-portal/data

# httpd
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/vpn-admin-portal.conf

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --bootstrap=tests/autoload.php

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-admin-portal(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/vpn-admin-portal || :

# remove template cache if it is there
rm -rf %{_localstatedir}/lib/vpn-admin-portal/*/tpl/* >/dev/null 2>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-admin-portal(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/vpn-admin-portal.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/vpn-admin-portal
%dir %attr(0750,root,apache) %{_sysconfdir}/vpn-admin-portal/default
%config(noreplace) %{_sysconfdir}/vpn-admin-portal/default/config.php
%{_bindir}/*
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Admin
%{_datadir}/vpn-admin-portal/web
%{_datadir}/vpn-admin-portal/data
%{_datadir}/vpn-admin-portal/views
%{_datadir}/vpn-admin-portal/config
%{_datadir}/vpn-admin-portal/locale
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/vpn-admin-portal
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE LICENSE.spdx

%changelog
* Wed Nov 28 2018 François Kooman <fkooman@tuxed.net> - 1.7.3-1
- update to 1.7.3

* Tue Oct 30 2018 François Kooman <fkooman@tuxed.net> - 1.7.2-1
- update to 1.7.2

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.7.1-1
- update to 1.7.1

* Sun Sep 09 2018 François Kooman <fkooman@tuxed.net> - 1.7.0-3
- merge dev and prod spec files in one
- cleanup requirements

* Sun Sep 09 2018 François Kooman <fkooman@tuxed.net> - 1.7.0-2
- add composer.json comments to (Build)Requires
- update composer dependencies
- move some stuff around to make it consistent with other spec files

* Wed Aug 15 2018 François Kooman <fkooman@tuxed.net> - 1.7.0-1
- update to 1.7.0

* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 1.6.1-1
- update to 1.6.1
- use PHPUnit 7 on supported platforms

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.6.0-3
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.6.0-2
- use fedora phpab template for generating autoloader

* Mon Jul 02 2018 François Kooman <fkooman@tuxed.net> - 1.6.0-1
- update to 1.6.0

* Fri Jun 29 2018 François Kooman <fkooman@tuxed.net> - 1.5.5-2
- use release tarball instead of Git tarball
- verify GPG signature

* Thu May 17 2018 François Kooman <fkooman@tuxed.net> - 1.5.5-1
- update to 1.5.5

* Wed May 16 2018 François Kooman <fkooman@tuxed.net> - 1.5.4-1
- update to 1.5.4

* Thu Mar 29 2018 François Kooman <fkooman@tuxed.net> - 1.5.3-1
- update to 1.5.3

* Fri Mar 16 2018 François Kooman <fkooman@tuxed.net> - 1.5.2-1
- update to 1.5.2

* Wed Feb 28 2018 François Kooman <fkooman@tuxed.net> - 1.5.1-1
- update to 1.5.1

* Sun Feb 25 2018 François Kooman <fkooman@tuxed.net> - 1.5.0-1
- update to 1.5.0

* Wed Jan 17 2018 François Kooman <fkooman@tuxed.net> - 1.4.1-1
- update to 1.4.1

* Sat Dec 23 2017 François Kooman <fkooman@tuxed.net> - 1.4.0-1
- update to 1.4.0
- cleanup autoloading

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 1.3.0-2
- use phpab to generate the classloader

* Tue Dec 05 2017 François Kooman <fkooman@tuxed.net> - 1.3.0-1
- update to 1.3.0

* Thu Nov 23 2017 François Kooman <fkooman@tuxed.net> - 1.2.0-1
- update to 1.2.0

* Tue Nov 14 2017 François Kooman <fkooman@tuxed.net> - 1.1.8-1
- update to 1.1.8

* Mon Oct 30 2017 François Kooman <fkooman@tuxed.net> - 1.1.7-1
- update to 1.1.7
- add LICENSE.spdx

* Mon Sep 11 2017 François Kooman <fkooman@tuxed.net> - 1.1.6-1
- update to 1.1.6

* Mon Sep 11 2017 François Kooman <fkooman@tuxed.net> - 1.1.5-1
- update to 1.1.5

* Sun Sep 10 2017 François Kooman <fkooman@tuxed.net> - 1.1.4-1
- update to 1.1.4

* Thu Aug 17 2017 François Kooman <fkooman@tuxed.net> - 1.1.3-1
- update to 1.1.3

* Thu Aug 17 2017 François Kooman <fkooman@tuxed.net> - 1.1.2-1
- update to 1.1.2

* Thu Aug 17 2017 François Kooman <fkooman@tuxed.net> - 1.1.1-1
- update to 1.1.1

* Thu Aug 17 2017 François Kooman <fkooman@tuxed.net> - 1.1.0-1
- update to 1.1.0
- add php-gd dependency
- add roboto-fontface-fonts dependency

* Tue Aug 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-3
- update httpd snippet

* Tue Jul 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- remove obsolete composer variables

* Thu Jul 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
