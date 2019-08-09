#global git 0c4c0e2b156cc41a38776baecaf1a0e01e76c9d9

Name:       php-saml-ds-artwork-eduVPN
Version:    2.0.0
Release:    2%{?dist}
Summary:    SAML Discovery Artwork for eduVPN
License:    AGPLv3+

URL:        https://github.com/eduvpn/disco-artwork
%if %{defined git}
Source0:    https://github.com/eduvpn/disco-artwork/archive/%{git}/disco-artwork-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/disco-artwork/releases/download/%{version}/php-saml-ds-artwork-eduVPN-%{version}.tar.xz
Source1:    https://github.com/eduvpn/disco-artwork/releases/download/%{version}/php-saml-ds-artwork-eduVPN-%{version}.tar.xz.minisig
Source2:    minisign-8466FFE127BCDC82.pub
%endif

BuildArch:  noarch

BuildRequires:  minisign

Requires:   php-saml-ds

%description
SAML Discovery Artwork for eduVPN.

%prep
%if %{defined git}
%setup -qn disco-artwork-%{git}
%else
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -p %{SOURCE2}
%setup -qn php-saml-ds-artwork-eduVPN-%{version}
%endif

%install
mkdir -p %{buildroot}%{_datadir}/php-saml-ds/views/eduVPN
mkdir -p %{buildroot}%{_datadir}/php-saml-ds/web/css/eduVPN
mkdir -p %{buildroot}%{_datadir}/php-saml-ds/web/img/eduVPN

cp -p css/eduvpn.css %{buildroot}%{_datadir}/php-saml-ds/web/css/eduVPN
cp -p img/eduvpn.png %{buildroot}%{_datadir}/php-saml-ds/web/img/eduVPN
cp -p views/*.php %{buildroot}%{_datadir}/php-saml-ds/views/eduVPN

%files
%defattr(-,root,root,-)
%{_datadir}/php-saml-ds/views/eduVPN
%{_datadir}/php-saml-ds/web/css/eduVPN
%{_datadir}/php-saml-ds/web/img/eduVPN
%doc README.md CHANGES.md

%changelog
* Fri Aug 09 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-2
- switch to minisign signature verification for release builds

* Wed Feb 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0

* Thu Sep 27 2018 François Kooman <fkooman@tuxed.net> - 1.0.1-5
- point to properly named release tarballs

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.0.1-4
- add missing BR gnupg2

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.0.1-3
- merge dev and prod spec files in one

* Sun Sep 09 2018 François Kooman <fkooman@tuxed.net> - 1.0.1-2
- use release tarball instead of Git tarball
- verify GPG signature

* Mon Jan 22 2018 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Mon Jan 22 2018 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
