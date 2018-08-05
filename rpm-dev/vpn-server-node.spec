%global composer_namespace      SURFnet/VPN/Node

%global github_owner            eduvpn
%global github_name             vpn-server-node
%global github_commit           6aa7105426ae02eaab25efc0a468c5f5698de928
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-server-node
Version:    1.0.18
Release:    1%{?dist}
Summary:    OpenVPN node controller

Group:      Applications/Internet
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz
Patch0:     %{name}-autoload.patch

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-filter
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  vpn-lib-common
BuildRequires:  php-composer(psr/log)

Requires:   php(language) >= 5.4.0
# the scripts in libexec/ and bin/ require the PHP CLI
Requires:   php-cli
Requires:   php-filter
Requires:   php-json
Requires:   php-mbstring
Requires:   php-pcre
Requires:   php-spl
Requires:   php-standard
Requires:   vpn-lib-common
Requires:   php-composer(psr/log)

Requires:   openvpn

Requires(post): policycoreutils-python
Requires(postun): policycoreutils-python

%description
OpenVPN node controller.

%prep
%setup -qn %{github_name}-%{github_commit} 
%patch0 -p1

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/Psr/Log/autoload.php';
require_once '%{_datadir}/php/SURFnet/VPN/Common/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Node
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Node

# bin
for i in certificate-info generate-firewall server-config
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_bindir}/%{name}-${i}
done

# libexec
for i in client-connect client-disconnect verify-otp
do
    install -m 0755 -D -p libexec/${i}.php %{buildroot}%{_libexecdir}/%{name}/${i}
done

mkdir -p %{buildroot}%{_sysconfdir}/%{name}/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/default/config.php
cp -pr config/firewall.php.example %{buildroot}%{_sysconfdir}/%{name}/firewall.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config
ln -s ../../../etc/openvpn/server %{buildroot}%{_datadir}/%{name}/openvpn-config

# legacy libexec symlinks
mkdir -p %{buildroot}%{_datadir}/%{name}/libexec
ln -s ../../../../usr/libexec/vpn-server-node/client-connect %{buildroot}%{_datadir}/%{name}/libexec/client-connect.php
ln -s ../../../../usr/libexec/vpn-server-node/client-disconnect %{buildroot}%{_datadir}/%{name}/libexec/client-disconnect.php
ln -s ../../../../usr/libexec/vpn-server-node/verify-otp %{buildroot}%{_datadir}/%{name}/libexec/verify-otp.php
ln -s ../../../usr/libexec/vpn-server-node/client-connect %{buildroot}%{_libexecdir}/%{name}-client-connect
ln -s ../../../usr/libexec/vpn-server-node/client-disconnect %{buildroot}%{_libexecdir}/%{name}-client-disconnect
ln -s ../../../usr/libexec/vpn-server-node/verify-otp %{buildroot}%{_libexecdir}/%{name}-verify-otp

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%defattr(-,root,root,-)
%dir %attr(0750,root,openvpn) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/firewall.php
%dir %attr(0750,root,openvpn) %{_sysconfdir}/%{name}/default
%config(noreplace) %{_sysconfdir}/%{name}/default/config.php
%{_bindir}/*
%{_libexecdir}/*
%dir %{_datadir}/%{name}
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Node
%{_datadir}/%{name}/config
%{_datadir}/%{name}/openvpn-config
# legacy libexec
%{_datadir}/%{name}/libexec
%doc README.md CHANGES.md composer.json config/config.php.example config/firewall.php.example
%license LICENSE LICENSE.spdx

%changelog
* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 1.0.18-1
- update to 1.0.18

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.0.17-3
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.0.17-2
- use fedora phpab template

* Mon Jul 02 2018 François Kooman <fkooman@tuxed.net> - 1.0.17-1
- update to 1.0.17

* Tue Jun 12 2018 François Kooman <fkooman@tuxed.net> - 1.0.16-1
- update to 1.0.16

* Wed Jun 06 2018 François Kooman <fkooman@tuxed.net> - 1.0.15-1
- update to 1.0.15

* Tue Apr 17 2018 François Kooman <fkooman@tuxed.net> - 1.0.14-1
- update to 1.0.14

* Thu Apr 12 2018 François Kooman <fkooman@tuxed.net> - 1.0.13-1
- update to 1.0.13

* Thu Apr 05 2018 François Kooman <fkooman@tuxed.net> - 1.0.12-1
- update to 1.0.12

* Thu Mar 29 2018 François Kooman <fkooman@tuxed.net> - 1.0.11-1
- update to 1.0.11

* Thu Mar 15 2018 François Kooman <fkooman@tuxed.net> - 1.0.10-1
- update to 1.0.10

* Sun Feb 25 2018 François Kooman <fkooman@tuxed.net> - 1.0.9-1
- update to 1.0.9

* Wed Jan 17 2018 François Kooman <fkooman@tuxed.net> - 1.0.8-1
- update to 1.0.8

* Sun Dec 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.7-1
- cleanup autoloading
- update to 1.0.7

* Fri Dec 15 2017 François Kooman <fkooman@tuxed.net> - 1.0.6-1
- update to 1.0.6

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.5-2
- use phpab to generate the classloader

* Mon Nov 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.5-1
- update to 1.0.5

* Wed Oct 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.4-1
- update to 1.0.4
- change handling of libexec and bin scripts by using changelogs
- add LICENSE.spdx

* Fri Oct 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-1
- update to 1.0.3

* Fri Sep 29 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Fri Jul 28 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Tue Jul 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- remove obsolete composer variables

* Thu Jul 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
