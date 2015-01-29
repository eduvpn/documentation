FROM centos:centos6
MAINTAINER François Kooman <fkooman@tuxed.net>

# Add EPEL
RUN yum -y install https://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm; yum clean all

# PHP base repo 
RUN curl -s -L -o /etc/yum.repos.d/fkooman-php-base-epel-6.repo https://copr.fedoraproject.org/coprs/fkooman/php-base/repo/epel-6/fkooman-php-base-epel-6.repo

# VPN management repo
RUN curl -s -L -o /etc/yum.repos.d/fkooman-vpn-management-epel-6.repo https://copr.fedoraproject.org/coprs/fkooman/vpn-management/repo/epel-6/fkooman-vpn-management-epel-6.repo

# Install updates
RUN yum -y update; yum clean all

# Install dependencies (and SSL module)
RUN yum install -y mod_ssl vpn-cert-service vpn-user-portal; yum clean all

# Allow connections from everywhere to the portal
RUN sed -i 's/Require local/Require all granted/' /etc/httpd/conf.d/vpn-user-portal.conf
RUN sed -i 's/Allow from 127.0.0.1/Allow from All/' /etc/httpd/conf.d/vpn-user-portal.conf
RUN sed -i 's/Allow from ::1//' /etc/httpd/conf.d/vpn-user-portal.conf

# "fake" a configured mellon by setting MELLON_NAME_ID so no need for a SAML IdP
RUN sed -i 's/#RequestHeader set MELLON_NAME_ID foo/RequestHeader set MELLON_NAME_ID foo/' /etc/httpd/conf.d/vpn-user-portal.conf

USER apache
# Init the databases
RUN vpn-cert-service-init
RUN vpn-user-portal-init

# Generate Server Configuration
#RUN vpn-cert-service-generate-server-config vpn.example.org

USER root

EXPOSE 443
# set httpd as entrypoint
ENTRYPOINT ["/usr/sbin/httpd"]
CMD ["-D", "FOREGROUND"]
