%global git 50dee1b82befbe584aa126446db62b2f9dc82490

Name:       vpn-portal-artwork-LC
Version:    2.0.0
Release:    0.2%{?dist}
Summary:    VPN Portal Artwork for LC
License:    AGPLv3+

URL:        https://github.com/letsconnectvpn/vpn-portal-artwork
%if %{defined git}
Source0:    https://github.com/letsconnectvpn/vpn-portal-artwork/archive/%{git}/vpn-portal-artwork-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/letsconnectvpn/vpn-portal-artwork/releases/download/%{version}/vpn-portal-artwork-LC-%{version}.tar.xz
Source1:    https://github.com/letsconnectvpn/vpn-portal-artwork/releases/download/%{version}/vpn-portal-artwork-LC-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif

BuildArch:  noarch

BuildRequires:  gnupg2

Requires:   vpn-user-portal

%description
VPN Portal Artwork for LC.

%prep
%if %{defined git}
%setup -qn vpn-portal-artwork-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
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
* Tue Feb 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.2
- rebuilt

* Sun Jan 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.1
- update to 2.0.0
