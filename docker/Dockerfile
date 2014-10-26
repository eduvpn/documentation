#FROM fedora:20
FROM centos:centos7
MAINTAINER François Kooman <fkooman@tuxed.net>
# Add EPEL repository (CentOS 7)
RUN yum -y install https://download.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-2.noarch.rpm; yum clean all
# Add php-oauth repository (Fedora, CentOS 7)
RUN curl -s -L -o /etc/yum.repos.d/fedora-php-oauth.repo https://repos.fedorapeople.org/repos/fkooman/php-oauth/fedora-php-oauth.repo
# Perform updates
RUN yum -y update; yum clean all
# Install dependencies (and SSL module)
RUN yum install -y mod_ssl mod_auth_mellon vpn-cert-service vpn-user-portal; yum clean all
# Allow connections from everywhere
RUN sed -i 's/Require local/Require all granted/' /etc/httpd/conf.d/vpn-cert-service.conf
RUN sed -i 's/Require local/Require all granted/' /etc/httpd/conf.d/vpn-user-portal.conf

USER apache
# Init
RUN vpn-cert-service-init
RUN vpn-user-portal-init

# Generate Server Configuration
# For production this is NOT a good idea, the configuration MUST be transported
# using secure means, and not by exposing it in /tmp and a web server
RUN vpn-cert-service-generate-server-config > /tmp/server.conf
USER root
# Copy the file to the web root (as root)
RUN cp /tmp/server.conf /var/www/html/server.conf
# Expose port 443 and set httpd as our entrypoint
EXPOSE 443
ENTRYPOINT ["/usr/sbin/httpd"]
CMD ["-D", "FOREGROUND"]
