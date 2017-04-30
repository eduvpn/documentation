%global composer_vendor         SURFnet
%global composer_project        vpn-server-node
%global composer_namespace      %{composer_vendor}/VPN/Node

%global github_owner            eduvpn
%global github_name             vpn-server-node
%global github_commit           c7ba18987a3b04067eecf7aa4fe5e9daf0d17d55
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-server-node
Version:    1.0.0
Release:    0.31%{?dist}
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

sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" bin/* libexec/*
sed -i "s|dirname(__DIR__)|'%{_datadir}/%{name}'|" bin/* libexec/*

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
mkdir -p %{buildroot}%{_datadir}/%{name}/src/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/%{name}/src/%{composer_namespace}

mkdir -p %{buildroot}%{_bindir}
(
cd bin
for phpFileName in $(ls *)
do
    binFileName=$(basename ${phpFileName} .php)
    cp -pr ${phpFileName} %{buildroot}%{_bindir}/%{name}-${binFileName}
    chmod 0755 %{buildroot}%{_bindir}/%{name}-${binFileName}
done
)

mkdir -p %{buildroot}%{_libexecdir}
(
cd libexec
for phpFileName in $(ls *)
do
    binFileName=$(basename ${phpFileName} .php)
    cp -pr ${phpFileName} %{buildroot}%{_libexecdir}/%{name}-${binFileName}
    chmod 0755 %{buildroot}%{_libexecdir}/%{name}-${binFileName}
done
)

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp -pr config/dh.pem %{buildroot}%{_sysconfdir}/%{name}
cp -pr config/firewall.php.example %{buildroot}%{_sysconfdir}/%{name}/firewall.php
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/default/config.php

ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config
ln -s ../../../etc/openvpn %{buildroot}%{_datadir}/%{name}/openvpn-config

%check
mkdir vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php',
));
\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Node\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --verbose

%files
%defattr(-,root,root,-)
%dir %attr(0750,root,openvpn) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/dh.pem
%config(noreplace) %{_sysconfdir}/%{name}/firewall.php
%dir %attr(0750,root,openvpn) %{_sysconfdir}/%{name}/default
%config(noreplace) %{_sysconfdir}/%{name}/default/config.php
%{_bindir}/*
%{_libexecdir}/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/src
%{_datadir}/%{name}/config
%{_datadir}/%{name}/openvpn-config
%doc README.md CHANGES.md composer.json config/config.php.example config/firewall.php.example config/dh.pem
%license LICENSE

%changelog
* Sun Apr 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.31
- rebuilt

* Wed Apr 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.30
- rebuilt

* Wed Apr 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.29
- rebuilt

* Fri Mar 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.28
- rebuilt

* Mon Mar 06 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.27
- rebuilt

* Fri Mar 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.26
- rebuilt

* Mon Feb 27 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.25
- rebuilt

* Tue Feb 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.24
- rebuilt

* Tue Jan 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.23
- rebuilt

* Thu Jan 05 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.22
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.21
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.20
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.19
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.18
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.17
- rebuilt

* Wed Dec 28 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.16
- rebuilt

* Fri Dec 16 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.15
- rebuilt

* Fri Dec 16 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.14
- rebuilt

* Fri Dec 16 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.13
- rebuilt

* Thu Dec 15 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.12
- rebuilt
