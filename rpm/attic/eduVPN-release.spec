Name:           eduVPN-release
Version:        1.0
Release:        0.1%{?dist}
Summary:        eduVPN package repository

License:        GPLv3+
URL:            https://repo.eduvpn.org
Source0:        https://repo.eduvpn.org/rpm/RPM-GPG-KEY-eduVPN   
Source1:        https://repo.eduvpn.org/rpm/eduVPN.repo

BuildArch:      noarch
  
%description
This package contains the eduVPN repository and GPG key.

%prep
%setup -q -c -T
install -pm 644 %{SOURCE0} .
install -pm 644 %{SOURCE1} .

%build


%install
rm -rf $RPM_BUILD_ROOT

install -Dpm 644 %{SOURCE0} \
    $RPM_BUILD_ROOT/%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-eduVPN
install -dm 755 $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d
install -pm 644 %{SOURCE1} \
    $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d

%files
%config(noreplace) /etc/yum.repos.d/*
/etc/pki/rpm-gpg/*

%changelog
* Fri Oct 13 2017 François Kooman <fkooman@tuxed.net>
- initial package
