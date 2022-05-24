#!/bin/sh

#
# Use Let's Encrypt to obtain certificates for the Web Server
#
# **NOTE** we assume you successfully performed deploy_debian.sh on your 
# server!
#

if ! [ "root" = "$(id -u -n)" ]; then
    echo "ERROR: ${0} must be run as root!"; exit 1
fi

###############################################################################
# VARIABLES
###############################################################################

MACHINE_HOSTNAME=$(hostname -f)

# DNS name of the Web Server
printf "DNS name of the Web Server [%s]: " "${MACHINE_HOSTNAME}"; read -r WEB_FQDN
WEB_FQDN=${WEB_FQDN:-${MACHINE_HOSTNAME}}
# convert hostname to lowercase
WEB_FQDN=$(echo "${WEB_FQDN}" | tr '[:upper:]' '[:lower:]')

###############################################################################
# SYSTEM
###############################################################################

apt install -y certbot

###############################################################################
# CERTBOT
###############################################################################

certbot certonly -d "${WEB_FQDN}" --webroot --webroot-path /var/www/html

###############################################################################
# APACHE
###############################################################################

sed -i "s|SSLCertificateFile /etc/ssl/certs/${WEB_FQDN}|#SSLCertificateFile /etc/ssl/certs/${WEB_FQDN}|" "/etc/apache2/sites-available/${WEB_FQDN}.conf"
sed -i "s|SSLCertificateKeyFile /etc/ssl/private/${WEB_FQDN}.key|#SSLCertificateKeyFile /etc/ssl/private/${WEB_FQDN}.key|" "/etc/apache2/sites-available/${WEB_FQDN}.conf"

sed -i "s|#SSLCertificateFile /etc/letsencrypt/live/${WEB_FQDN}/cert.pem|SSLCertificateFile /etc/letsencrypt/live/${WEB_FQDN}/cert.pem|" "/etc/apache2/sites-available/${WEB_FQDN}.conf"
sed -i "s|#SSLCertificateKeyFile /etc/letsencrypt/live/${WEB_FQDN}/privkey.pem|SSLCertificateKeyFile /etc/letsencrypt/live/${WEB_FQDN}/privkey.pem|" "/etc/apache2/sites-available/${WEB_FQDN}.conf"
sed -i "s|#SSLCertificateChainFile /etc/letsencrypt/live/${WEB_FQDN}/chain.pem|SSLCertificateChainFile /etc/letsencrypt/live/${WEB_FQDN}/chain.pem|" "/etc/apache2/sites-available/${WEB_FQDN}.conf"

systemctl reload apache2

###############################################################################
# HOOK
###############################################################################

# make sure to gracefully restart Apache after a certificate has been
# renewed...
cat << EOF > /etc/letsencrypt/renewal-hooks/post/restart_apache.sh
#!/bin/sh
systemctl reload apache2
EOF

chmod +x /etc/letsencrypt/renewal-hooks/post/restart_apache.sh
