%global git da60a8a88a8a373be546499323543383336af3e0

Name:       vpn-portal-artwork-LC
Version:    1.4.0
Release:    0.3%{?dist}
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
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/views/LC
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/css/LC
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/img/LC

cp -p css/LC.css %{buildroot}%{_datadir}/vpn-user-portal/web/css/LC
cp -p img/LC.png %{buildroot}%{_datadir}/vpn-user-portal/web/img/LC
cp -p views/vpn-user-portal/*.php %{buildroot}%{_datadir}/vpn-user-portal/views/LC

%files
%defattr(-,root,root,-)
%{_datadir}/vpn-user-portal/views/LC
%{_datadir}/vpn-user-portal/web/css/LC
%{_datadir}/vpn-user-portal/web/img/LC
%doc CHANGES.md README.md

%changelog
* Sun Jan 13 2019 François Kooman <fkooman@tuxed.net> - 1.4.0-0.3
- rebuilt

* Wed Jan 09 2019 François Kooman <fkooman@tuxed.net> - 1.4.0-0.2
- rebuilt

* Fri Dec 14 2018 François Kooman <fkooman@tuxed.net> - 1.4.0-0.1
- update to 1.4.0

* Wed Nov 28 2018 François Kooman <fkooman@tuxed.net> - 1.3.0-1
- update to 1.3.0

* Wed Oct 03 2018 François Kooman <fkooman@tuxed.net> - 1.2.0-1
- update to 1.2.0

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.1.2-2
- merge dev and prod spec files in one

* Fri Sep 07 2018 François Kooman <fkooman@tuxed.net> - 1.1.2-1
- update to 1.1.2

* Mon Jul 02 2018 François Kooman <fkooman@tuxed.net> - 1.1.1-2
- use release tarball instead of Git tarball
- verify GPG signature

* Thu May 24 2018 François Kooman <fkooman@tuxed.net> - 1.1.1-1
- update to 1.1.1

* Tue Jan 02 2018 François Kooman <fkooman@tuxed.net> - 1.1.0-2
- artwork moved to own repository

* Tue Dec 05 2017 François Kooman <fkooman@tuxed.net> - 1.1.0-1
- update for template refactor

* Mon Nov 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- no longer include README/CHANGES

* Mon Nov 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
