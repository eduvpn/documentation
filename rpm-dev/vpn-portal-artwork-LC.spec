%global git e360fe203cc1ed34aca7d62fcdd278f36a0a2a42

Name:       vpn-portal-artwork-LC
Version:    2.0.2
Release:    0.6%{?dist}
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
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/locale/LC
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/css/LC
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/img/LC

cp -p css/*.css %{buildroot}%{_datadir}/vpn-user-portal/web/css/LC
cp -p img/*.png %{buildroot}%{_datadir}/vpn-user-portal/web/img/LC
cp -p locale/*.php %{buildroot}%{_datadir}/vpn-user-portal/locale/LC
cp -p views/*.php %{buildroot}%{_datadir}/vpn-user-portal/views/LC

%files
%defattr(-,root,root,-)
%{_datadir}/vpn-user-portal/views/LC
%{_datadir}/vpn-user-portal/locale/LC
%{_datadir}/vpn-user-portal/web/css/LC
%{_datadir}/vpn-user-portal/web/img/LC
%doc CHANGES.md README.md

%changelog
* Thu Oct 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.2-0.6
- rebuilt

* Thu Oct 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.2-0.5
- rebuilt

* Mon Oct 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.2-0.4
- rebuilt

* Mon Oct 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.2-0.3
- rebuilt

* Sun Sep 29 2019 François Kooman <fkooman@tuxed.net> - 2.0.2-0.2
- rebuilt

* Thu Sep 26 2019 François Kooman <fkooman@tuxed.net> - 2.0.2-0.1
- update to 2.0.2

* Mon Aug 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.1-1
- update to 2.0.1

* Fri Aug 09 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-2
- switch to minisign signature verification for release builds

* Mon Apr 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0
