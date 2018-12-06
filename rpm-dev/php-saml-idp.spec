%global git a525c3949130edfea1c59df064c50a469a220172

Name:       php-saml-idp
Version:    0.0.0
Release:    0.12%{?dist}
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
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/SAML/IdP
cp -pr web %{buildroot}%{_datadir}/%{name}

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%dir %{_datadir}/php/fkooman
%dir %{_datadir}/php/fkooman/SAML
%{_datadir}/php/fkooman/SAML/IdP
%{_datadir}/%{name}/web
%{_datadir}/%{name}/config
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE

%changelog
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
