FROM centos:centos6
MAINTAINER François Kooman <fkooman@tuxed.net>

# Add EPEL
RUN yum -y install https://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm; yum clean all

# enable CR
RUN yum -y install centos-release-cr; yum clean all

# Add eduVPN repository
RUN curl -s -L -o /etc/yum.repos.d/eduVPN.repo https://www.php-oauth.net/repo/eduVPN/eduVPN.repo

# Install updates
RUN yum -y update; yum clean all

# Install dependencies (and SSL module)
RUN yum install -y mod_ssl openvpn vpn-cert-service vpn-user-portal; yum clean all

# Allow connections from everywhere to the portal
RUN sed -i 's/Require local/Require all granted/' /etc/httpd/conf.d/vpn-user-portal.conf
RUN sed -i 's/Allow from 127.0.0.1/Allow from All/' /etc/httpd/conf.d/vpn-user-portal.conf
RUN sed -i 's/Allow from ::1//' /etc/httpd/conf.d/vpn-user-portal.conf
RUN sed -i 's/#RequestHeader set MELLON_NAME_ID foo/RequestHeader set MELLON_NAME_ID foo/' /etc/httpd/conf.d/vpn-user-portal.conf

USER apache
# Init the databases
RUN vpn-cert-service-init
RUN vpn-user-portal-init
# Generate Server Configuration
RUN vpn-cert-service-generate-server-config > /tmp/server.conf

USER root
# Copy the file to the web root (as root)
RUN cp /tmp/server.conf /etc/openvpn/server.conf
RUN chmod 600 /etc/openvpn/server.conf
RUN rm /tmp/server.conf
# Expose port 443 and 1194
EXPOSE 443
EXPOSE 1194
# set httpd as entrypoint
ENTRYPOINT ["/usr/sbin/httpd"]
CMD ["-D", "FOREGROUND"]
