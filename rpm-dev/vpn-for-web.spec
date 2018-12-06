%global git 437668d76ba987f3fccceb32d715761aa7f0bf94

Name:       vpn-for-web
Version:    0.1.0
Release:    0.2%{?dist}
Summary:    VPN for Web
Group:      Applications/Internet
License:    AGPLv3+
URL:        https://github.com/eduvpn/vpn-for-web
%if %{defined git}
Source0:    https://github.com/eduvpn/vpn-for-web/archive/%{git}/vpn-for-web-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/vpn-for-web/releases/download/%{version}/vpn-for-web-%{version}.tar.xz
Source1:    https://github.com/eduvpn/vpn-for-web/releases/download/%{version}/vpn-for-web-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif
Source3:    vpn-for-web-httpd.conf
Patch0:     vpn-for-web-autoload.patch

BuildArch:  noarch

BuildRequires:  gnupg2
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
#    "require-dev": {
#        "phpunit/phpunit": "^4.8.35|^5|^6|^7"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  phpunit7
%global phpunit %{_bindir}/phpunit7
%else
BuildRequires:  phpunit
%global phpunit %{_bindir}/phpunit
%endif
#    "require": {
#        "ext-filter": "*",
#        "ext-imagick": "*",
#        "ext-json": "*",
#        "ext-mbstring": "*",
#        "ext-pcre": "*",
#        "ext-spl": "*",
#        "fkooman/oauth2-client": "^7",
#        "fkooman/secookie": "^2",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "php": ">= 5.4.0",
#        "twig/twig": "^1.0"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-filter
BuildRequires:  php-imagick
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  php-composer(fkooman/oauth2-client)
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(twig/twig) < 2

%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif
#    "require": {
#        "ext-filter": "*",
#        "ext-imagick": "*",
#        "ext-json": "*",
#        "ext-mbstring": "*",
#        "ext-pcre": "*",
#        "ext-spl": "*",
#        "fkooman/oauth2-client": "^7",
#        "fkooman/secookie": "^2",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "php": ">= 5.4.0",
#        "twig/twig": "^1.0"
#    },
Requires:   php(language) >= 5.4.0
Requires:   php-cli
Requires:   php-filter
Requires:   php-imagick
Requires:   php-json
Requires:   php-mbstring
Requires:   php-pcre
Requires:   php-spl
Requires:   php-composer(fkooman/oauth2-client)
Requires:   php-composer(fkooman/secookie)
Requires:   php-composer(paragonie/constant_time_encoding)
Requires:   php-composer(twig/twig) < 2

Requires(post): /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage

%description
VPN for Web.

%prep
%if %{defined git}
%setup -qn vpn-for-web-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn vpn-for-web-%{version}
%endif
%patch0 -p1

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/fkooman/OAuth/Client/autoload.php';
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
require_once '%{_datadir}/php/Twig/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/vpn-for-web
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Web
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Web
install -m 0755 -D -p bin/fetch-provider-info.php %{buildroot}%{_bindir}/vpn-for-web-fetch-provider-info
cp -pr web views %{buildroot}%{_datadir}/vpn-for-web

mkdir -p %{buildroot}%{_sysconfdir}/vpn-for-web
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/vpn-for-web/config.php
ln -s ../../../etc/vpn-for-web %{buildroot}%{_datadir}/vpn-for-web/config

mkdir -p %{buildroot}%{_localstatedir}/lib/vpn-for-web
ln -s ../../../var/lib/vpn-for-web %{buildroot}%{_datadir}/vpn-for-web/data

# httpd
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/vpn-for-web.conf

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-for-web(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/vpn-for-web || :

# remove template cache if it is there
rm -rf %{_localstatedir}/lib/vpn-for-web/*/tpl/* >/dev/null 2>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-for-web(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/vpn-for-web.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/vpn-for-web
%config(noreplace) %{_sysconfdir}/vpn-for-web/config.php
%{_bindir}/*
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Web
%{_datadir}/vpn-for-web/web
%{_datadir}/vpn-for-web/data
%{_datadir}/vpn-for-web/views
%{_datadir}/vpn-for-web/config
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/vpn-for-web
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE LICENSE.spdx

%changelog
* Wed Nov 28 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.2
- rebuilt

* Wed Nov 28 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.1
- initial package
