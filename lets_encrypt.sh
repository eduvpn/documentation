#!/bin/sh

#
# Use Let's Encrypt
#

###############################################################################
# VARIABLES
###############################################################################

WEB_FQDN=vpn.example

# TOS: https://letsencrypt.org/repository/
AGREE_TOS=""
# to agree to the TOS, add "#" the line above and remove "#" below this line
#AGREE_TOS="--agree-tos"

# The email address you want to use for Let's Encrypt (for issues with 
# renewing the certificate etc.)
LETSENCRYPT_MAIL=admin@example.org

###############################################################################
# SYSTEM
###############################################################################

PACKAGE_MANAGER=/usr/bin/yum

# install and enable remi repository
${PACKAGE_MANAGER} install -y certbot

# stop Apache
systemctl stop httpd

###############################################################################
# CERTBOT
###############################################################################

certbot register ${AGREE_TOS} --no-eff-email -m ${LETSENCRYPT_MAIL}
certbot certonly -n --standalone -d ${WEB_FQDN}

cat << EOF > /etc/sysconfig/certbot
PRE_HOOK="--pre-hook 'systemctl stop httpd'"
POST_HOOK="--post-hook 'systemctl start httpd'"
RENEW_HOOK=""
CERTBOT_ARGS=""
EOF

# enable automatic renewal
systemctl enable --now certbot-renew.timer

###############################################################################
# APACHE
###############################################################################

sed -i "s|SSLCertificateFile /etc/pki/tls/certs/${WEB_FQDN}|#SSLCertificateFile /etc/pki/tls/certs/${WEB_FQDN}|" /etc/httpd/conf.d/${WEB_FQDN}.conf
sed -i "s|SSLCertificateKeyFile /etc/pki/tls/private/${WEB_FQDN}.key|#SSLCertificateKeyFile /etc/pki/tls/private/${WEB_FQDN}.key|" /etc/httpd/conf.d/${WEB_FQDN}.conf

sed -i "s|#SSLCertificateFile /etc/letsencrypt/live/${WEB_FQDN}/cert.pem|SSLCertificateFile /etc/letsencrypt/live/${WEB_FQDN}/cert.pem|" /etc/httpd/conf.d/${WEB_FQDN}.conf
sed -i "s|#SSLCertificateKeyFile /etc/letsencrypt/live/${WEB_FQDN}/privkey.pem|SSLCertificateKeyFile /etc/letsencrypt/live/${WEB_FQDN}/privkey.pem|" /etc/httpd/conf.d/${WEB_FQDN}.conf
sed -i "s|#SSLCertificateChainFile /etc/letsencrypt/live/${WEB_FQDN}/chain.pem|SSLCertificateChainFile /etc/letsencrypt/live/${WEB_FQDN}/chain.pem|" /etc/httpd/conf.d/${WEB_FQDN}.conf

###############################################################################
# CLEANUP
###############################################################################

# start Apache
systemctl start httpd

# ALL DONE!
