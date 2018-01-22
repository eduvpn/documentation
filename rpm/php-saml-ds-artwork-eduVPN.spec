%global github_owner            eduVPN
%global github_name             disco-artwork
%global github_commit           0c5e2e1b43c215a790205498be301dcb4c515754
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

%global style_name              eduVPN

Name:       php-saml-ds-artwork-%{style_name}
Version:    1.0.0
Release:    1%{?dist}
Summary:    SAML Discovery Artwork for %{style_name}
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

Requires:   php-saml-ds

%description
SAML Discovery Artwork for %{style_name}.

%prep
%setup -qn %{github_name}-%{github_commit} 

%install
mkdir -p %{buildroot}%{_datadir}/php-saml-ds/views/%{style_name}
mkdir -p %{buildroot}%{_datadir}/php-saml-ds/web/css/%{style_name}
mkdir -p %{buildroot}%{_datadir}/php-saml-ds/web/img/%{style_name}

cp -p css/eduvpn.css %{buildroot}%{_datadir}/php-saml-ds/web/css/%{style_name}
cp -p img/eduvpn.png %{buildroot}%{_datadir}/php-saml-ds/web/img/%{style_name}
cp -p views/*.twig %{buildroot}%{_datadir}/php-saml-ds/views/%{style_name}

%post
# clear template cache
rm -rf %{_localstatedir}/lib/php-saml-ds/tpl/* >/dev/null 2>/dev/null || :

%postun
# clear template cache
rm -rf %{_localstatedir}/lib/php-saml-ds/tpl/* >/dev/null 2>/dev/null || :

%files
%defattr(-,root,root,-)
%{_datadir}/php-saml-ds/views/%{style_name}
%{_datadir}/php-saml-ds/web/css/%{style_name}
%{_datadir}/php-saml-ds/web/img/%{style_name}
%doc README.md CHANGES.md

%changelog
* Mon Jan 22 2018 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
