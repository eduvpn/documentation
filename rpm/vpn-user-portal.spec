%global composer_vendor         eduvpn
%global composer_project        vpn-user-portal
%global composer_namespace      SURFnet/VPN/Portal

%global github_owner            eduvpn
%global github_name             vpn-user-portal
%global github_commit           cb48cf6f88254741ee728ad9b657117cb1bb4295
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-user-portal
Version:    1.0.0
Release:    0.92%{?dist}
Summary:    VPN User Portal

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
BuildRequires:  php-filter
BuildRequires:  php-gettext
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  php-libsodium
BuildRequires:  vpn-lib-common
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  php-composer(twig/twig) < 2
BuildRequires:  php-composer(twig/extensions)
BuildRequires:  php-composer(bacon/bacon-qr-code)
BuildRequires:  php-composer(fkooman/oauth2-client)
BuildRequires:  php-composer(fkooman/oauth2-server)

Requires:   php(language) >= 5.4.0
# the scripts in bin/ require the PHP CLI
Requires:   php-cli
Requires:   php-date
Requires:   php-filter
Requires:   php-gettext
Requires:   php-hash
Requires:   php-json
Requires:   php-mbstring
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-libsodium
Requires:   php-spl
Requires:   vpn-lib-common
Requires:   php-composer(fedora/autoloader)
Requires:   php-composer(twig/twig) < 2
Requires:   php-composer(twig/extensions)
Requires:   php-composer(bacon/bacon-qr-code)
Requires:   php-composer(fkooman/oauth2-client)
Requires:   php-composer(fkooman/oauth2-server)

%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif

Requires(post): /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage

%description
VPN User Portal.

%prep
%setup -qn %{github_name}-%{github_commit} 

sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" bin/*
sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" web/*.php
sed -i "s|dirname(__DIR__)|'%{_datadir}/%{name}'|" bin/*

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Portal\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/SURFnet/VPN/Common/autoload.php',
    '%{_datadir}/php/Twig/autoload.php',
    '%{_datadir}/php/Twig/Extensions/autoload.php',
    '%{_datadir}/php/BaconQrCode/autoload.php',
    '%{_datadir}/php/fkooman/OAuth/Client/autoload.php',
    '%{_datadir}/php/fkooman/OAuth/Server/autoload.php',
));
AUTOLOAD

%install
install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

mkdir -p %{buildroot}%{_datadir}/%{name}
cp -pr web views locale %{buildroot}%{_datadir}/%{name}
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

mkdir -p %{buildroot}%{_sysconfdir}/%{name}/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/default/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

%check
phpunit --bootstrap=%{buildroot}/%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php

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
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/src
%{_datadir}/%{name}/data
%{_datadir}/%{name}/web
%{_datadir}/%{name}/views
%{_datadir}/%{name}/config
%{_datadir}/%{name}/locale
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE

%changelog
* Thu Mar 16 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.92
- rebuilt

* Thu Mar 16 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.91
- rebuilt

* Wed Mar 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.90
- rebuilt

* Wed Mar 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.89
- rebuilt

* Thu Mar 02 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.88
- rebuilt

* Thu Feb 23 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.87
- rebuilt

* Mon Feb 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.86
- rebuilt

* Tue Feb 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.85
- rebuilt

* Tue Feb 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.84
- rebuilt

* Mon Feb 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.83
- rebuilt

* Mon Feb 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.82
- rebuilt

* Tue Feb 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.81
- rebuilt

* Tue Feb 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.80
- rebuilt

* Tue Feb 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.79
- rebuilt

* Thu Feb 02 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.78
- rebuilt

* Tue Jan 31 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.77
- rebuilt

* Thu Jan 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.76
- rebuilt

* Thu Jan 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.75
- rebuilt

* Wed Jan 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.74
- rebuilt

* Wed Jan 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.73
- rebuilt

* Mon Jan 23 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.72
- rebuilt

* Mon Jan 23 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.71
- rebuilt

* Mon Jan 23 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.70
- rebuilt

* Mon Jan 23 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.69
- rebuilt

* Sun Jan 22 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.68
- rebuilt

* Sun Jan 22 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.67
- rebuilt

* Fri Jan 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.66
- rebuilt

* Fri Jan 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.65
- rebuilt

* Fri Jan 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.64
- rebuilt

* Fri Jan 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.63
- rebuilt
