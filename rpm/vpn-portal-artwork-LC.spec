%global style_name              LC

Name:       vpn-portal-artwork-%{style_name}
Version:    1.1.2
Release:    1%{?dist}
Summary:    VPN Portal Artwork for %{style_name}
License:    AGPLv3+

URL:        https://github.com/letsconnectvpn/vpn-portal-artwork
Source0:    https://github.com/letsconnectvpn/vpn-portal-artwork/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:    https://github.com/letsconnectvpn/vpn-portal-artwork/releases/download/%{version}/%{name}-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2

BuildArch:  noarch

BuildRequires:  gnupg2

Requires:   vpn-user-portal
Requires:   vpn-admin-portal

%description
VPN Portal Artwork for %{style_name}.

%prep
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn vpn-portal-artwork-%{style_name}-%{version}

%install
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/views/%{style_name}
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/css/%{style_name}
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal/web/img/%{style_name}
mkdir -p %{buildroot}%{_datadir}/vpn-admin-portal/views/%{style_name}
mkdir -p %{buildroot}%{_datadir}/vpn-admin-portal/web/css/%{style_name}
mkdir -p %{buildroot}%{_datadir}/vpn-admin-portal/web/img/%{style_name}

cp -p css/%{style_name}.css %{buildroot}%{_datadir}/vpn-user-portal/web/css/%{style_name}
cp -p css/%{style_name}.css %{buildroot}%{_datadir}/vpn-admin-portal/web/css/%{style_name}
cp -p img/%{style_name}.png %{buildroot}%{_datadir}/vpn-user-portal/web/img/%{style_name}
cp -p img/%{style_name}.png %{buildroot}%{_datadir}/vpn-admin-portal/web/img/%{style_name}
cp -p views/vpn-user-portal/*.twig %{buildroot}%{_datadir}/vpn-user-portal/views/%{style_name}
cp -p views/vpn-admin-portal/*.twig %{buildroot}%{_datadir}/vpn-admin-portal/views/%{style_name}

%post
# clear template cache
rm -rf %{_localstatedir}/lib/vpn-user-portal/*/tpl/* >/dev/null 2>/dev/null || :
rm -rf %{_localstatedir}/lib/vpn-admin-portal/*/tpl/* >/dev/null 2>/dev/null || :

%postun
# clear template cache
rm -rf %{_localstatedir}/lib/vpn-user-portal/*/tpl/* >/dev/null 2>/dev/null || :
rm -rf %{_localstatedir}/lib/vpn-admin-portal/*/tpl/* >/dev/null 2>/dev/null || :

%files
%defattr(-,root,root,-)
%{_datadir}/vpn-user-portal/views/%{style_name}
%{_datadir}/vpn-user-portal/web/css/%{style_name}
%{_datadir}/vpn-user-portal/web/img/%{style_name}
%{_datadir}/vpn-admin-portal/views/%{style_name}
%{_datadir}/vpn-admin-portal/web/css/%{style_name}
%{_datadir}/vpn-admin-portal/web/img/%{style_name}
%doc CHANGES.md README.md

%changelog
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
