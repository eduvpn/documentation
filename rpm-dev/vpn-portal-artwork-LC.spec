%global github_owner            letsconnectvpn
%global github_name             vpn-portal-artwork
%global github_commit           6ac538130f6d8aab8b0103c5a11df6bca49c2710
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

%global style_name              LC

Name:       vpn-portal-artwork-%{style_name}
Version:    1.1.2
Release:    1%{?dist}
Summary:    VPN Portal Artwork for %{style_name}
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

Requires:   vpn-user-portal
Requires:   vpn-admin-portal

%description
VPN Portal Artwork for %{style_name}.

%prep
%setup -qn %{github_name}-%{github_commit} 

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

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.1.1-2
- use fedora phpab template

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
