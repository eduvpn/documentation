#global git 39e22cec84ec88b4e687648cc1f5ec6c6d9f7c6c

Name:       vpn-portal-artwork-LC
Version:    2.0.0
Release:    2%{?dist}
Summary:    VPN Portal Artwork for LC
License:    AGPLv3+

URL:        https://github.com/letsconnectvpn/vpn-portal-artwork
%if %{defined git}
Source0:    https://github.com/letsconnectvpn/vpn-portal-artwork/archive/%{git}/vpn-portal-artwork-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/letsconnectvpn/vpn-portal-artwork/releases/download/%{version}/vpn-portal-artwork-LC-%{version}.tar.xz
Source1:    https://github.com/letsconnectvpn/vpn-portal-artwork/releases/download/%{version}/vpn-portal-artwork-LC-%{version}.tar.xz.minisig
Source2:    minisign-8466FFE127BCDC82.pub
%endif

BuildArch:  noarch

BuildRequires:  minisign

Requires:   vpn-user-portal

%description
VPN Portal Artwork for LC.

%prep
%if %{defined git}
%setup -qn vpn-portal-artwork-%{git}
%else
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -p %{SOURCE2}
%setup -qn vpn-portal-artwork-LC-%{version}
%endif

%install
mkdir -p %{buildroot}%{_sysconfdir}/vpn-user-portal
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/views/LC
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/css/LC
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/img/LC

cp -p config/LC.php.example %{buildroot}%{_sysconfdir}/vpn-user-portal/LC.php
cp -p css/LC.css %{buildroot}%{_datadir}/vpn-user-portal/web/css/LC
cp -p img/LC.png %{buildroot}%{_datadir}/vpn-user-portal/web/img/LC
cp -p views/vpn-user-portal/*.php %{buildroot}%{_datadir}/vpn-user-portal/views/LC

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/vpn-user-portal/LC.php
%{_datadir}/vpn-user-portal/views/LC
%{_datadir}/vpn-user-portal/web/css/LC
%{_datadir}/vpn-user-portal/web/img/LC
%doc CHANGES.md README.md

%changelog
* Fri Aug 09 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-2
- switch to minisign signature verification for release builds

* Mon Apr 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0
