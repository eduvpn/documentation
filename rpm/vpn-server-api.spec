%global composer_namespace      SURFnet/VPN/Server

%global github_owner            eduvpn
%global github_name             vpn-server-api
%global github_commit           0bfb114827bd0fab16a675a1b69ecd6213433fe1
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-server-api
Version:    1.2.0
Release:    2%{?dist}
Summary:    Web service to control OpenVPN processes

Group:      Applications/Internet
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz
Source1:    %{name}-httpd.conf
Source2:    %{name}.cron
BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

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
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab
BuildRequires:  vpn-lib-common
BuildRequires:  php-composer(psr/log)
BuildRequires:  php-composer(christian-riesen/otp)
BuildRequires:  php-composer(fkooman/yubitwee)
BuildRequires:  php-composer(fkooman/oauth2-client)

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
Requires:   php-composer(christian-riesen/otp)
Requires:   php-composer(fkooman/yubitwee)
Requires:   php-composer(fkooman/oauth2-client)

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
%setup -qn %{github_name}-%{github_commit} 

# remove bundled Easy RSA 3.x
%if 0%{?fedora} >= 24
rm -rf easy-rsa
%endif

%build
%{_bindir}/phpab -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/Otp/autoload.php';
require_once '%{_datadir}/php/Psr/Log/autoload.php';
require_once '%{_datadir}/php/fkooman/YubiTwee/autoload.php';
require_once '%{_datadir}/php/fkooman/OAuth/Client/autoload.php';
require_once '%{_datadir}/php/SURFnet/VPN/Common/autoload.php';
AUTOLOAD

%install
install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

mkdir -p %{buildroot}%{_datadir}/%{name}
cp -pr src web %{buildroot}%{_datadir}/%{name}

mkdir -p %{buildroot}%{_datadir}/%{name}/bin
install -D -p bin/* %{buildroot}%{_datadir}/%{name}/bin
mkdir -p %{buildroot}%{_bindir}
# create symlinks
for i in housekeeping init show-instance-info stats status update-api-secrets update-ip
do
    ln -s %{_datadir}/%{name}/bin/${i}.php %{buildroot}%{_bindir}/%{name}-${i}
done

mkdir -p %{buildroot}%{_sysconfdir}/%{name}/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/default/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

# Easy RSA
%if 0%{?fedora} >= 24
ln -s ../../../usr/share/easy-rsa/3 %{buildroot}%{_datadir}/%{name}/easy-rsa
%else 
cp -pr easy-rsa %{buildroot}%{_datadir}/%{name}
%endif 

# cron
mkdir -p %{buildroot}%{_sysconfdir}/cron.d
%{__install} -p -D -m 0640 %{SOURCE2} %{buildroot}%{_sysconfdir}/cron.d/%{name}

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

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
%{_datadir}/%{name}/src
%{_datadir}/%{name}/bin
%{_datadir}/%{name}/web
%{_datadir}/%{name}/easy-rsa
%{_datadir}/%{name}/config
%{_datadir}/%{name}/data
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md composer.json config/config.php.example CHANGES.md
%license LICENSE LICENSE.spdx

%changelog
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
