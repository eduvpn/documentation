%global git e7d5370ffd939e0995add22520c724fbebbeb71f

Name:       php-saml-idp
Version:    0.0.0
Release:    0.62%{?dist}
Summary:    SAML IdP

Group:      Applications/Internet
License:    ASL2.0

URL:        https://software.tuxed.net/php-saml-idp
%if %{defined git}
Source0:    https://git.tuxed.net/fkooman/php-saml-idp/snapshot/php-saml-idp-%{git}.tar.xz
%else
Source0:    https://software.tuxed.net/php-saml-idp/files/php-saml-idp-%{version}.tar.xz
Source1:    https://software.tuxed.net/php-saml-idp/files/php-saml-idp-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif
Source3:    %{name}-httpd.conf
Patch0:     %{name}-autoload.patch

BuildArch:  noarch

BuildRequires:  gnupg2
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
#    "require": {
#        "ext-date": "*",
#        "ext-dom": "*",
#        "ext-hash": "*",
#        "ext-libxml": "*",
#        "ext-openssl": "*",
#        "ext-spl": "*",
#        "ext-zlib": "*",
#        "fkooman/secookie": "^2",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "php": ">=5.4"
#    }
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-dom
BuildRequires:  php-hash
BuildRequires:  php-libxml
BuildRequires:  php-openssl
BuildRequires:  php-spl
BuildRequires:  php-zlib
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(ircmaxell/password-compat)
BuildRequires:  php-composer(symfony/polyfill-php56)
%endif

%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif
#    "require": {
#        "ext-date": "*",
#        "ext-dom": "*",
#        "ext-hash": "*",
#        "ext-libxml": "*",
#        "ext-openssl": "*",
#        "ext-spl": "*",
#        "ext-zlib": "*",
#        "fkooman/secookie": "^2",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "php": ">=5.4"
#    }
Requires:   php(language) >= 5.4.0
Requires:   php-cli
Requires:   php-date
Requires:   php-dom
Requires:   php-hash
Requires:   php-libxml
Requires:   php-openssl
Requires:   php-spl
Requires:   php-zlib
Requires:   php-composer(fkooman/secookie)
Requires:   php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
Requires:   php-composer(paragonie/random_compat)
Requires:   php-composer(ircmaxell/password-compat)
Requires:   php-composer(symfony/polyfill-php56)
%endif

%description
SAML IdP written in PHP.

%prep
%if %{defined git}
%setup -qn php-saml-idp-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn php-saml-idp-%{version}
%endif
%patch0 -p1

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{_datadir}/php/password_compat/password.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/php/fkooman/SAML/IdP
install -m 0755 -D -p bin/generate-salt.php %{buildroot}%{_bindir}/php-saml-idp-generate-salt
install -m 0755 -D -p bin/add-user.php %{buildroot}%{_bindir}/php-saml-idp-add-user
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/SAML/IdP
cp -pr schema views locale web %{buildroot}%{_datadir}/%{name}

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/config.php
cp -pr config/metadata.php.example %{buildroot}%{_sysconfdir}/%{name}/metadata.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%config(noreplace) %{_sysconfdir}/%{name}/metadata.php
%{_bindir}/*
%dir %{_datadir}/php/fkooman
%dir %{_datadir}/php/fkooman/SAML
%{_datadir}/php/fkooman/SAML/IdP
%{_datadir}/%{name}/web
%{_datadir}/%{name}/views
%{_datadir}/%{name}/locale
%{_datadir}/%{name}/schema
%{_datadir}/%{name}/config
%doc README.md CHANGES.md composer.json config/config.php.example config/metadata.php.example
%license LICENSE

%changelog
* Sun Jan 20 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.62
- rebuilt

* Tue Jan 08 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.61
- rebuilt

* Wed Jan 02 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.60
- rebuilt

* Sun Dec 30 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.59
- rebuilt

* Thu Dec 27 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.58
- rebuilt

* Wed Dec 26 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.57
- rebuilt

* Wed Dec 26 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.56
- rebuilt

* Wed Dec 26 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.55
- rebuilt

* Wed Dec 26 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.54
- rebuilt

* Wed Dec 26 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.53
- rebuilt

* Wed Dec 26 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.52
- rebuilt

* Wed Dec 26 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.51
- rebuilt

* Wed Dec 26 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.50
- rebuilt

* Wed Dec 26 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.49
- rebuilt

* Mon Dec 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.48
- rebuilt

* Mon Dec 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.47
- rebuilt

* Sun Dec 23 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.46
- rebuilt

* Sun Dec 23 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.45
- rebuilt

* Sun Dec 23 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.44
- rebuilt

* Sun Dec 23 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.43
- rebuilt

* Sun Dec 23 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.42
- rebuilt

* Sun Dec 23 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.41
- rebuilt

* Sun Dec 23 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.40
- rebuilt

* Sun Dec 23 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.39
- rebuilt

* Sat Dec 22 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.38
- rebuilt

* Sat Dec 22 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.37
- rebuilt

* Sat Dec 22 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.36
- rebuilt

* Fri Dec 21 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.35
- rebuilt

* Fri Dec 21 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.34
- rebuilt

* Thu Dec 20 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.33
- rebuilt

* Wed Dec 19 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.32
- rebuilt

* Wed Dec 19 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.31
- rebuilt

* Wed Dec 19 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.30
- rebuilt

* Wed Dec 19 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.29
- rebuilt

* Wed Dec 19 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.28
- rebuilt

* Wed Dec 19 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.27
- rebuilt

* Wed Dec 19 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.26
- rebuilt

* Wed Dec 19 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.25
- rebuilt

* Wed Dec 19 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.24
- rebuilt

* Tue Dec 18 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.23
- rebuilt

* Tue Dec 18 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.22
- rebuilt

* Tue Dec 18 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.21
- rebuilt

* Tue Dec 18 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.20
- rebuilt

* Tue Dec 18 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.19
- rebuilt

* Tue Dec 18 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.18
- rebuilt

* Mon Dec 17 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.17
- rebuilt

* Mon Dec 17 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.16
- rebuilt

* Mon Dec 17 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.15
- rebuilt

* Mon Dec 17 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.14
- rebuilt

* Mon Dec 17 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.13
- rebuilt

* Thu Sep 27 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.12
- rebuilt

* Mon Sep 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.11
- rebuilt

* Mon Sep 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.10
- rebuilt

* Mon Sep 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.9
- rebuilt

* Mon Sep 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.8
- rebuilt

* Mon Sep 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.7
- rebuilt

* Mon Sep 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.6
- rebuilt

* Mon Sep 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.5
- rebuilt

* Mon Sep 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.4
- rebuilt

* Mon Sep 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.3
- rebuilt

* Mon Sep 24 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.2
- rebuilt

* Sat Sep 22 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.1
- initial package
