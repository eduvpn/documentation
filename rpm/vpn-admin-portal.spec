%global composer_namespace      SURFnet/VPN/Admin

%global github_owner            eduvpn
%global github_name             vpn-admin-portal
%global github_commit           9a6d6b0591eff6cadde369d1b204b5e153f5b7e5
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-admin-portal
Version:    1.2.0
Release:    1%{?dist}
Summary:    VPN Admin Portal

Group:      Applications/Internet
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz
Source1:    %{name}-httpd.conf

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

BuildRequires:  %{_bindir}/phpunit
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-spl
BuildRequires:  php-gd
BuildRequires:  php-gettext
BuildRequires:  vpn-lib-common
BuildRequires:  php-composer(twig/twig) < 2
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(fedora/autoloader)

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
Requires:   php-composer(fedora/autoloader)
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
%setup -qn %{github_name}-%{github_commit} 

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Admin\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/SURFnet/VPN/Common/autoload.php',
    '%{_datadir}/php/fkooman/SeCookie/autoload.php',
    '%{_datadir}/php/Twig/autoload.php',
));
AUTOLOAD

%install
install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

mkdir -p %{buildroot}%{_datadir}/%{name}
cp -pr bin src web views locale %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_bindir}

chmod +x %{buildroot}/%{_datadir}/%{name}/bin/add-user.php
ln -s %{_datadir}/%{name}/bin/add-user.php %{buildroot}%{_bindir}/%{name}-add-user

mkdir -p %{buildroot}%{_sysconfdir}/%{name}/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/default/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

%check
cat << 'EOF' | tee tests/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/%{name}/src/autoload.php',
));
\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Admin\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --bootstrap=tests/autoload.php

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
%{_datadir}/%{name}/src
%{_datadir}/%{name}/web
%{_datadir}/%{name}/data
%{_datadir}/%{name}/bin
%{_datadir}/%{name}/views
%{_datadir}/%{name}/config
%{_datadir}/%{name}/locale
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE LICENSE.spdx

%changelog
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
