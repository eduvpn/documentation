#global git 747d0193df8db699bb900a6694d7a45d66bb6fcb

Name:       vpn-portal-artwork-eduVPN
Version:    2.0.1
Release:    1%{?dist}
Summary:    VPN Portal Artwork for eduVPN
License:    AGPLv3+

URL:        https://github.com/eduvpn/vpn-portal-artwork
%if %{defined git}
Source0:    https://github.com/eduvpn/vpn-portal-artwork/archive/%{git}/vpn-portal-artwork-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/vpn-portal-artwork/releases/download/%{version}/vpn-portal-artwork-eduVPN-%{version}.tar.xz
Source1:    https://github.com/eduvpn/vpn-portal-artwork/releases/download/%{version}/vpn-portal-artwork-eduVPN-%{version}.tar.xz.minisig
Source2:    minisign-8466FFE127BCDC82.pub
%endif

BuildArch:  noarch

BuildRequires:  minisign

Requires:   vpn-user-portal

%description
VPN Portal Artwork for eduVPN.

%prep
%if %{defined git}
%setup -qn vpn-portal-artwork-%{git}
%else
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -p %{SOURCE2}
%setup -qn vpn-portal-artwork-eduVPN-%{version}
%endif

%install
mkdir -p %{buildroot}%{_sysconfdir}/vpn-user-portal
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/views/eduVPN
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/css/eduVPN
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/img/eduVPN

cp -p css/eduVPN.css %{buildroot}%{_datadir}/vpn-user-portal/web/css/eduVPN
cp -p img/eduVPN.png %{buildroot}%{_datadir}/vpn-user-portal/web/img/eduVPN
cp -p views/vpn-user-portal/*.php %{buildroot}%{_datadir}/vpn-user-portal/views/eduVPN

%files
%defattr(-,root,root,-)
%{_datadir}/vpn-user-portal/views/eduVPN
%{_datadir}/vpn-user-portal/web/css/eduVPN
%{_datadir}/vpn-user-portal/web/img/eduVPN
%doc CHANGES.md README.md

%changelog
* Mon Aug 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.1-1
- update to 2.0.1

* Fri Aug 09 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-2
- switch to minisign signature verification for release builds

* Mon Apr 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0
