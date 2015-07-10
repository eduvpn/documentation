FROM centos:latest
MAINTAINER François Kooman <fkooman@tuxed.net>

# Add EPEL
RUN yum -y install https://download.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm

# PHP base repo 
RUN curl -s -L -o /etc/yum.repos.d/fkooman-php-base-epel-7.repo https://copr.fedoraproject.org/coprs/fkooman/php-base/repo/epel-7/fkooman-php-base-epel-7.repo

# VPN management repo
RUN curl -s -L -o /etc/yum.repos.d/fkooman-vpn-management-epel-7.repo https://copr.fedoraproject.org/coprs/fkooman/vpn-management/repo/epel-7/fkooman-vpn-management-epel-7.repo

# Install updates
RUN yum -y update; yum clean all

# Install dependencies (and SSL module)
RUN yum install -y mod_ssl vpn-cert-service vpn-user-portal vpn-crl-fetcher; yum clean all

# Allow connections from everywhere to the portal
RUN sed -i 's/Require local/Require all granted/' /etc/httpd/conf.d/vpn-user-portal.conf

# "fake" a configured mellon by setting MELLON-NAME-ID so no need for a SAML IdP
RUN sed -i 's/#RequestHeader set MELLON-NAME-ID foo/RequestHeader set MELLON-NAME-ID foo/' /etc/httpd/conf.d/vpn-user-portal.conf

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
