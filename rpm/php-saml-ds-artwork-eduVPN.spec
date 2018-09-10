#global git c735ec8ce841cc0334d7c61c1b1f2685af1ed9a8

Name:       php-saml-ds-artwork-eduVPN
Version:    1.0.1
Release:    3%{?dist}
Summary:    SAML Discovery Artwork for eduVPN
License:    AGPLv3+

URL:        https://github.com/eduvpn/disco-artwork
%if %{defined git}
Source0:    https://github.com/eduvpn/disco-artwork/archive/%{git}/disco-artwork-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/disco-artwork/releases/download/%{version}/disco-artwork-%{version}.tar.xz
Source1:    https://github.com/eduvpn/disco-artwork/releases/download/%{version}/disco-artwork-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif

BuildArch:  noarch

Requires:   php-saml-ds

%description
SAML Discovery Artwork for eduVPN.

%prep
%if %{defined git}
%setup -qn disco-artwork-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn disco-artwork-%{version}
%endif

%install
mkdir -p %{buildroot}%{_datadir}/php-saml-ds/views/eduVPN
mkdir -p %{buildroot}%{_datadir}/php-saml-ds/web/css/eduVPN
mkdir -p %{buildroot}%{_datadir}/php-saml-ds/web/img/eduVPN

cp -p css/eduvpn.css %{buildroot}%{_datadir}/php-saml-ds/web/css/eduVPN
cp -p img/eduvpn.png %{buildroot}%{_datadir}/php-saml-ds/web/img/eduVPN
cp -p views/*.twig %{buildroot}%{_datadir}/php-saml-ds/views/eduVPN

%post
# clear template cache
rm -rf %{_localstatedir}/lib/php-saml-ds/tpl/* >/dev/null 2>/dev/null || :

%postun
# clear template cache
rm -rf %{_localstatedir}/lib/php-saml-ds/tpl/* >/dev/null 2>/dev/null || :

%files
%defattr(-,root,root,-)
%{_datadir}/php-saml-ds/views/eduVPN
%{_datadir}/php-saml-ds/web/css/eduVPN
%{_datadir}/php-saml-ds/web/img/eduVPN
%doc README.md CHANGES.md

%changelog
* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.0.1-3
- merge dev and prod spec files in one

* Sun Sep 09 2018 François Kooman <fkooman@tuxed.net> - 1.0.1-2
- use release tarball instead of Git tarball
- verify GPG signature

* Mon Jan 22 2018 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Mon Jan 22 2018 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
