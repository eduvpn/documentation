# Apache mod_md

**NOTE**: I am experimenting with this since 2021-08-08!

It is possible to manage SSL certificates from Let's Encrypt through Apache 
directly with [mod_md](https://httpd.apache.org/docs/2.4/mod/mod_md.html) 
without the need for `certbot`. This should make things more robust.

```
$ sudo dnf -y install mod_md
```

In `/etc/httpd/conf.d/vpn.example.org.conf`, outside the `<VirtualHost>`:

```
MDomain vpn.example.org
MDContactEmail admin@example.org
MDCertificateAgreement accepted
MDStapling on
```

From the `<VirtualHost>` section you can remove the following lines:

```
SSLCertificateChainFile
SSLCertificateFile
SSLCertificateKeyFile
```

You can remove the following lines from `/etc/httpd/conf.d/ssl.conf`:

```
SSLUseStapling          on
SSLStaplingResponderTimeout 5
SSLStaplingReturnResponderErrors off
SSLStaplingCache shmcb:/run/httpd/ssl_stapling(128000)
```

Restart Apache:

```
$ sudo systemctl restart httpd && sleep 5 && sudo systemctl reload httpd
```

On the first (re)start the certificat is obtained from Let's Encrypt, after
that succeeds a (graceful) restart is required in order to active the 
certificate.

Now hopefully all works as expected on renew!

### Cleaning

Remove `certbot`:

```
$ sudo dnf remove certbot
```

Remove the directory `/etc/letsencrypt` and the file 
`/etc/sysconfig/certbot.rpmsave`.
