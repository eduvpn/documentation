Name:       vpn-admin-portal
Version:    1.6.0
Release:    1%{?dist}
Summary:    VPN Admin Portal
Group:      Applications/Internet
License:    AGPLv3+
URL:        https://github.com/eduvpn/%{name}
Source0:    https://github.com/eduvpn/%{name}/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:    https://github.com/eduvpn/%{name}/releases/download/%{version}/%{name}-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
Source3:    %{name}-httpd.conf
Patch0:     %{name}-autoload.patch

BuildArch:  noarch

BuildRequires:  gnupg2
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-spl
BuildRequires:  php-gd
BuildRequires:  php-gettext
BuildRequires:  vpn-lib-common
BuildRequires:  php-composer(twig/twig) < 2
BuildRequires:  php-composer(fkooman/secookie)

Requires:   roboto-fontface-fonts
Requires:   php(language) >= 5.4.0
# the scripts in bin/ require the PHP CLI
Requires:   php-cli
Requires:   php-date
Requires:   php-spl
Requires:   php-gd
Requires:   php-gettext
Requires:   vpn-lib-common
Requires:   php-composer(twig/twig) < 2
Requires:   php-composer(fkooman/secookie)
%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif

Requires(post): /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage

%description
VPN Admin Portal.

%prep
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn %{name}-%{version}
%patch0 -p1

%build
%{_bindir}/phpab -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/SURFnet/VPN/Common/autoload.php';
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/Twig/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Admin
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Admin
install -m 0755 -D -p bin/add-user.php %{buildroot}%{_bindir}/%{name}-add-user
cp -pr web views locale %{buildroot}%{_datadir}/%{name}

mkdir -p %{buildroot}%{_sysconfdir}/%{name}/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/default/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

# httpd
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --bootstrap=tests/autoload.php

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/%{name} || :

# remove template cache if it is there
rm -rf %{_localstatedir}/lib/%{name}/*/tpl/* >/dev/null 2>/dev/null || :

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
%{_bindir}/*
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Admin
%{_datadir}/%{name}/web
%{_datadir}/%{name}/data
%{_datadir}/%{name}/views
%{_datadir}/%{name}/config
%{_datadir}/%{name}/locale
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE LICENSE.spdx

%changelog
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
