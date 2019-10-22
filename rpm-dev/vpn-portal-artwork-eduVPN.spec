%global git 6fdc0b0ac82a35ae6141b44220a459135b81f8a7

Name:       vpn-portal-artwork-eduVPN
Version:    2.0.3
Release:    0.28%{?dist}
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
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/locale/eduVPN
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/css/eduVPN
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/img/eduVPN

cp -p css/*.css %{buildroot}%{_datadir}/vpn-user-portal/web/css/eduVPN
cp -p img/*.png %{buildroot}%{_datadir}/vpn-user-portal/web/img/eduVPN
cp -p locale/*.php %{buildroot}%{_datadir}/vpn-user-portal/locale/eduVPN
cp -p views/*.php %{buildroot}%{_datadir}/vpn-user-portal/views/eduVPN

%files
%defattr(-,root,root,-)
%{_datadir}/vpn-user-portal/views/eduVPN
%{_datadir}/vpn-user-portal/locale/eduVPN
%{_datadir}/vpn-user-portal/web/css/eduVPN
%{_datadir}/vpn-user-portal/web/img/eduVPN
%doc CHANGES.md README.md

%changelog
* Tue Oct 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.28
- rebuilt

* Tue Oct 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.27
- rebuilt

* Sat Oct 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.26
- rebuilt

* Thu Oct 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.25
- rebuilt

* Thu Oct 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.24
- rebuilt

* Wed Oct 16 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.23
- rebuilt

* Wed Oct 16 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.22
- rebuilt

* Tue Oct 08 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.21
- rebuilt

* Tue Oct 08 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.20
- rebuilt

* Tue Oct 08 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.19
- rebuilt

* Tue Oct 08 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.18
- rebuilt

* Mon Oct 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.17
- rebuilt

* Mon Oct 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.16
- rebuilt

* Mon Oct 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.15
- rebuilt

* Sun Sep 29 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.14
- rebuilt

* Fri Sep 27 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.13
- rebuilt

* Thu Sep 26 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.12
- rebuilt

* Tue Sep 24 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.11
- rebuilt

* Thu Sep 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.10
- rebuilt

* Thu Sep 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.9
- rebuilt

* Tue Sep 10 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.8
- rebuilt

* Tue Sep 10 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.7
- rebuilt

* Tue Sep 10 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.6
- rebuilt

* Tue Sep 10 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.5
- rebuilt

* Tue Sep 10 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.4
- rebuilt

* Wed Aug 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.3
- rebuilt

* Tue Aug 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.2
- rebuilt

* Tue Aug 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-0.1
- update to 2.0.3

* Tue Aug 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.2-1
- update to 2.0.2

* Mon Aug 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.1-1
- update to 2.0.1

* Fri Aug 09 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-2
- switch to minisign signature verification for release builds

* Mon Apr 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0
