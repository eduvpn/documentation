%global composer_namespace      SURFnet/VPN/Portal

%global github_owner            eduvpn
%global github_name             vpn-user-portal
%global github_commit           becf3baa543c2df80d04b9d7fbf2f037bd0a39fd
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-user-portal
Version:    1.5.4
Release:    1%{?dist}
Summary:    VPN User Portal

Group:      Applications/Internet
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz
Source1:    %{name}-httpd.conf
Source2:    %{name}.cron
Patch0:     %{name}-autoload.patch

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-gettext
BuildRequires:  php-hash
BuildRequires:  php-json
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
%if 0%{?fedora} >= 28
BuildRequires:  php-sodium
%else
BuildRequires:  php-libsodium
%endif
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  vpn-lib-common
BuildRequires:  php-composer(bacon/bacon-qr-code)
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(fkooman/oauth2-client)
BuildRequires:  php-composer(fkooman/oauth2-server)
BuildRequires:  php-composer(paragonie/random_compat)

Requires:   crontabs
Requires:   php(language) >= 5.4.0
# the scripts in bin/ require the PHP CLI
Requires:   php-cli
Requires:   php-date
Requires:   php-filter
Requires:   php-gettext
Requires:   php-hash
Requires:   php-json
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
%if 0%{?fedora} >= 28
Requires:       php-sodium
%else
Requires:       php-libsodium
%endif
Requires:   php-mbstring
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-spl
Requires:   vpn-lib-common
Requires:   php-composer(bacon/bacon-qr-code)
Requires:   php-composer(fkooman/secookie)
Requires:   php-composer(fkooman/oauth2-client)
Requires:   php-composer(fkooman/oauth2-server)
Requires:   php-composer(paragonie/random_compat)

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
%patch0 -p1

%build
%{_bindir}/phpab -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once sprintf('%s/sodium_compat.php', __DIR__);
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{_datadir}/php/SURFnet/VPN/Common/autoload.php';
require_once '%{_datadir}/php/BaconQrCode/autoload.php';
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/fkooman/OAuth/Client/autoload.php';
require_once '%{_datadir}/php/fkooman/OAuth/Server/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Portal
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Portal

for i in add-user foreign-key-list-fetcher init show-public-key generate-voucher
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_bindir}/%{name}-${i}
done

cp -pr web views locale %{buildroot}%{_datadir}/%{name}

mkdir -p %{buildroot}%{_sysconfdir}/%{name}/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/default/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

# cron
mkdir -p %{buildroot}%{_sysconfdir}/cron.d
%{__install} -p -D -m 0640 %{SOURCE2} %{buildroot}%{_sysconfdir}/cron.d/%{name}

# httpd
install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

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
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%{_bindir}/*
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Portal
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/data
%{_datadir}/%{name}/web
%{_datadir}/%{name}/views
%{_datadir}/%{name}/config
%{_datadir}/%{name}/locale
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE LICENSE.spdx

%changelog
* Fri Mar 16 2018 François Kooman <fkooman@tuxed.net> - 1.5.4-1
- update to 1.5.4

* Thu Mar 15 2018 François Kooman <fkooman@tuxed.net> - 1.5.3-1
- update to 1.5.3

* Wed Feb 28 2018 François Kooman <fkooman@tuxed.net> - 1.5.2-1
- update to 1.5.2

* Mon Feb 26 2018 François Kooman <fkooman@tuxed.net> - 1.5.1-1
- update to 1.5.1
- install generate-voucher script as well

* Sun Feb 25 2018 François Kooman <fkooman@tuxed.net> - 1.5.0-1
- update to 1.5.0

* Tue Feb 06 2018 François Kooman <fkooman@tuxed.net> - 1.4.9-1
- update to 1.4.9

* Wed Jan 24 2018 François Kooman <fkooman@tuxed.net> - 1.4.8-1
- update to 1.4.8

* Mon Jan 22 2018 François Kooman <fkooman@tuxed.net> - 1.4.7-1
- update to 1.4.7

* Wed Jan 10 2018 François Kooman <fkooman@tuxed.net> - 1.4.6-1
- update to 1.4.6

* Thu Dec 28 2017 François Kooman <fkooman@tuxed.net> - 1.4.5-1
- update to 1.4.5

* Sat Dec 23 2017 François Kooman <fkooman@tuxed.net> - 1.4.4-1
- update to 1.4.4

* Thu Dec 14 2017 François Kooman <fkooman@tuxed.net> - 1.4.3-1
- update to 1.4.3

* Tue Dec 12 2017 François Kooman <fkooman@tuxed.net> - 1.4.2-1
- cleanup autoloader
- update to 1.4.2

* Fri Dec 08 2017 François Kooman <fkooman@tuxed.net> - 1.4.1-1
- update to 1.4.1
- use phpab to generate the classloader

* Tue Dec 05 2017 François Kooman <fkooman@tuxed.net> - 1.4.0-1
- update to 1.4.0

* Thu Nov 30 2017 François Kooman <fkooman@tuxed.net> - 1.3.2-1
- update to 1.3.2

* Wed Nov 29 2017 François Kooman <fkooman@tuxed.net> - 1.3.1-1
- update to 1.3.1

* Tue Nov 28 2017 François Kooman <fkooman@tuxed.net> - 1.3.0-1
- update to 1.3.0

* Thu Nov 23 2017 François Kooman <fkooman@tuxed.net> - 1.2.0-1
- update to 1.2.0

* Mon Nov 20 2017 François Kooman <fkooman@tuxed.net> - 1.1.1-1
- update to 1.1.1

* Tue Nov 14 2017 François Kooman <fkooman@tuxed.net> - 1.1.0-1
- update to 1.1.0

* Mon Nov 06 2017 François Kooman <fkooman@tuxed.net> - 1.0.10-1
- update to 1.0.10

* Thu Oct 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.9-1
- add paragonie/random_compat dependency
- update to 1.0.9
- pick the right sodium depending on OS
- cleanup web and bin script installation (using symlinks)
- add LICENSE.spdx

* Tue Oct 24 2017 François Kooman <fkooman@tuxed.net> - 1.0.8-1
- update to 1.0.8

* Tue Oct 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.7-1
- update to 1.0.7

* Mon Sep 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.6-1
- update to 1.0.6

* Thu Sep 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.5-1
- update to 1.0.5

* Mon Sep 11 2017 François Kooman <fkooman@tuxed.net> - 1.0.4-1
- update to 1.0.4

* Mon Sep 11 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-1
- update to 1.0.3

* Sun Sep 10 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Thu Aug 24 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Tue Aug 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-3
- update httpd snippet

* Tue Jul 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- remove obsolete composer variables

* Thu Jul 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
