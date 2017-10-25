%global composer_namespace      SURFnet/VPN/Node

%global github_owner            eduvpn
%global github_name             vpn-server-node
%global github_commit           7aaa36ce1be71d7da5af9c14169edb6a32c30713
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-server-node
Version:    1.0.4
Release:    1%{?dist}
Summary:    OpenVPN node controller

Group:      Applications/Internet
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

BuildRequires:  %{_bindir}/phpunit
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-filter
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  vpn-lib-common
BuildRequires:  php-composer(fedora/autoloader)
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
Requires:   php-composer(fedora/autoloader)
Requires:   php-composer(psr/log)

Requires:   openvpn

Requires(post): policycoreutils-python
Requires(postun): policycoreutils-python

%description
OpenVPN node controller.

%prep
%setup -qn %{github_name}-%{github_commit} 

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Node\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/Psr/Log/autoload.php',
    '%{_datadir}/php/SURFnet/VPN/Common/autoload.php',
));
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

# old libexec path (backwards compatible with old server configs)
ln -s %{_datadir}/%{name}/libexec/client-connect.php %{buildroot}%{_libexecdir}/%{name}-client-connect
ln -s %{_datadir}/%{name}/libexec/client-disconnect.php %{buildroot}%{_libexecdir}/%{name}-client-disconnect
ln -s %{_datadir}/%{name}/libexec/verify-otp.php %{buildroot}%{_libexecdir}/%{name}-verify-otp

# new path
ln -s %{_datadir}/%{name}/libexec/client-connect.php %{buildroot}%{_libexecdir}/%{name}/client-connect
ln -s %{_datadir}/%{name}/libexec/client-disconnect.php %{buildroot}%{_libexecdir}/%{name}/client-disconnect
ln -s %{_datadir}/%{name}/libexec/verify-otp.php %{buildroot}%{_libexecdir}/%{name}/verify-otp

%check
cat << 'EOF' | tee tests/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/%{name}/src/autoload.php',
));
\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Node\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --bootstrap tests/autoload.php

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
