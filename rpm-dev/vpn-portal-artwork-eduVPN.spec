%global git 64601833ce31236a9da582d99b788e6f68c2db62

Name:       vpn-portal-artwork-eduVPN
Version:    2.0.0
Release:    0.2%{?dist}
Summary:    VPN Portal Artwork for eduVPN
License:    AGPLv3+

URL:        https://github.com/eduvpn/vpn-portal-artwork
%if %{defined git}
Source0:    https://github.com/eduvpn/vpn-portal-artwork/archive/%{git}/vpn-portal-artwork-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/vpn-portal-artwork/releases/download/%{version}/vpn-portal-artwork-eduVPN-%{version}.tar.xz
Source1:    https://github.com/eduvpn/vpn-portal-artwork/releases/download/%{version}/vpn-portal-artwork-eduVPN-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif

BuildArch:  noarch

BuildRequires:  gnupg2

Requires:   vpn-user-portal

%description
VPN Portal Artwork for eduVPN.

%prep
%if %{defined git}
%setup -qn vpn-portal-artwork-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn vpn-portal-artwork-eduVPN-%{version}
%endif

%install
mkdir -p %{buildroot}%{_sysconfdir}/vpn-user-portal
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/views/eduVPN
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/css/eduVPN
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/img/eduVPN

cp -p config/eduVPN.php.example %{buildroot}%{_sysconfdir}/vpn-user-portal/eduVPN.php
cp -p css/eduVPN.css %{buildroot}%{_datadir}/vpn-user-portal/web/css/eduVPN
cp -p img/eduVPN.png %{buildroot}%{_datadir}/vpn-user-portal/web/img/eduVPN
cp -p views/vpn-user-portal/*.php %{buildroot}%{_datadir}/vpn-user-portal/views/eduVPN

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/vpn-user-portal/eduVPN.php
%{_datadir}/vpn-user-portal/views/eduVPN
%{_datadir}/vpn-user-portal/web/css/eduVPN
%{_datadir}/vpn-user-portal/web/img/eduVPN
%doc CHANGES.md README.md

%changelog
* Tue Feb 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.2
- rebuilt

* Sun Jan 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.1
- update to 2.0.0
