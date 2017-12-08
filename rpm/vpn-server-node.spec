%global composer_namespace      SURFnet/VPN/Node

%global github_owner            eduvpn
%global github_name             vpn-server-node
%global github_commit           0a169d0ce772c9d28ea8294e751ae6bd04d3c21a
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-server-node
Version:    1.0.5
Release:    2%{?dist}
Summary:    OpenVPN node controller

Group:      Applications/Internet
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

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

%build
%{_bindir}/phpab -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/Psr/Log/autoload.php';
require_once '%{_datadir}/php/SURFnet/VPN/Common/autoload.php';
AUTOLOAD

%install

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/default
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
#mkdir -p %{buildroot}%{_datadir}/%{name}/openvpn-config

cp -pr bin libexec src %{buildroot}%{_datadir}/%{name}
chmod 0755 %{buildroot}%{_datadir}/%{name}/libexec/*
chmod 0755 %{buildroot}%{_datadir}/%{name}/bin/*

cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/default/config.php
cp -pr config/firewall.php.example %{buildroot}%{_sysconfdir}/%{name}/firewall.php

ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config
ln -s ../../../etc/openvpn/server %{buildroot}%{_datadir}/%{name}/openvpn-config

ln -s %{_datadir}/%{name}/bin/generate-firewall.php %{buildroot}%{_bindir}/%{name}-generate-firewall
ln -s %{_datadir}/%{name}/bin/server-config.php %{buildroot}%{_bindir}/%{name}-server-config
ln -s %{_datadir}/%{name}/bin/certificate-info.php %{buildroot}%{_bindir}/%{name}-certificate-info

# old libexec path (backwards compatible with old server configs)
ln -s %{_datadir}/%{name}/libexec/client-connect.php %{buildroot}%{_libexecdir}/%{name}-client-connect
ln -s %{_datadir}/%{name}/libexec/client-disconnect.php %{buildroot}%{_libexecdir}/%{name}-client-disconnect
ln -s %{_datadir}/%{name}/libexec/verify-otp.php %{buildroot}%{_libexecdir}/%{name}-verify-otp

# new path
ln -s %{_datadir}/%{name}/libexec/client-connect.php %{buildroot}%{_libexecdir}/%{name}/client-connect
ln -s %{_datadir}/%{name}/libexec/client-disconnect.php %{buildroot}%{_libexecdir}/%{name}/client-disconnect
ln -s %{_datadir}/%{name}/libexec/verify-otp.php %{buildroot}%{_libexecdir}/%{name}/verify-otp

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
%{_datadir}/%{name}/src
%{_datadir}/%{name}/bin
%{_datadir}/%{name}/libexec
%{_datadir}/%{name}/config
%{_datadir}/%{name}/openvpn-config
%doc README.md CHANGES.md composer.json config/config.php.example config/firewall.php.example
%license LICENSE LICENSE.spdx

%changelog
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
