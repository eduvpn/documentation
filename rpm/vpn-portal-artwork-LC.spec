%global github_owner            letsconnectvpn
%global github_name             artwork
%global github_commit           3a3bb8d49cba4c465abd8fda115eb875ae03ee37
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

%global style_name              LC

Name:       vpn-portal-artwork-%{style_name}
Version:    1.0.0
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

cp -p portal/css/%{style_name}.css %{buildroot}%{_datadir}/vpn-user-portal/web/css/%{style_name}
cp -p portal/css/%{style_name}.css %{buildroot}%{_datadir}/vpn-admin-portal/web/css/%{style_name}
cp -p portal/img/%{style_name}.png %{buildroot}%{_datadir}/vpn-user-portal/web/img/%{style_name}
cp -p portal/img/%{style_name}.png %{buildroot}%{_datadir}/vpn-admin-portal/web/img/%{style_name}
cp -p portal/views/*.twig %{buildroot}%{_datadir}/vpn-user-portal/views/%{style_name}
cp -p portal/views/*.twig %{buildroot}%{_datadir}/vpn-admin-portal/views/%{style_name}

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
%doc portal/README.md portal/CHANGES.md

%changelog
* Mon Nov 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
