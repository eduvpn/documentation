%global git 94550097530b87c0d77ab1b5738ae1fc7dd0c403

Name:       vpn-portal-artwork-eduVPN
Version:    1.4.0
Release:    0.4%{?dist}
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
* Sun Jan 13 2019 François Kooman <fkooman@tuxed.net> - 1.4.0-0.4
- rebuilt

* Wed Jan 09 2019 François Kooman <fkooman@tuxed.net> - 1.4.0-0.3
- rebuilt

* Fri Dec 14 2018 François Kooman <fkooman@tuxed.net> - 1.4.0-0.2
- rebuilt

* Fri Dec 14 2018 François Kooman <fkooman@tuxed.net> - 1.4.0-0.1
- update to 1.4.0

* Wed Nov 28 2018 François Kooman <fkooman@tuxed.net> - 1.3.0-1
- update to 1.3.0

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.2.3-1
- update to 1.2.3

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.2.2-3
- merge dev and prod spec files in one

* Mon Jul 02 2018 François Kooman <fkooman@tuxed.net> - 1.2.2-2
- use release tarball instead of Git tarball
- verify GPG signature
- include README/CHANGES

* Thu May 24 2018 François Kooman <fkooman@tuxed.net> - 1.2.2-1
- update to 1.2.2

* Tue Jan 23 2018 François Kooman <fkooman@tuxed.net> - 1.2.1-1
- update to 1.2.1

* Mon Jan 22 2018 François Kooman <fkooman@tuxed.net> - 1.2.0-1
- update to 1.2.0

* Tue Jan 02 2018 François Kooman <fkooman@tuxed.net> - 1.1.0-2
- artwork moved to separate repository

* Tue Dec 05 2017 François Kooman <fkooman@tuxed.net> - 1.1.0-1
- update for template refactor

* Mon Nov 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-3
- bump release

* Mon Nov 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- no longer include README/CHANGES

* Mon Nov 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
