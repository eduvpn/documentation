# Deploying on CentOS

For simple one server deployments and tests, we have a deploy script available 
you can run on a fresh CentOS 7 installation. It will configure all components 
and will be ready for use after running!

Additional scripts are available after deployment:

* Use [Let's Encrypt](https://letsencrypt.org/) for automatic web server 
  certificate management;
* Switch to modern PHP (experimental)

## Requirements

* Clean CentOS 7 installation with all updates installed;
* SELinux MUST be enabled 
  ([CentOS SELinux](https://wiki.centos.org/HowTos/SELinux));
* Network equipment allows access to the very least `tcp/80`, `tcp/443`, 
  `udp/1194` and `tcp/1194` for basic functionality;

We test only with the official CentOS 
[Minimal ISO](https://centos.org/download/) and the official 
[Cloud](https://wiki.centos.org/Download) images.

If you have a more complicated setup, we recommend to manually walk through 
the deploy script and follow the steps.

## Base Deploy

Perform these steps on the host where you want to deploy:

    $ curl -L -O https://github.com/eduvpn/documentation/archive/master.tar.gz
    $ tar -xzf master.tar.gz
    $ cd documentation-master

Run the script (as root):

    $ sudo -s
    # ./deploy.sh

Specify the hostname you want to use for your VPN server. Both the "Web" and 
"OpenVPN" DNS names can be identical for simple 1 machine setups.

## Configuration

### VPN

See [PROFILE_CONFIG](PROFILE_CONFIG.md) on how to update the VPN server 
settings.

### Authentication 

#### Username & Password

By default there is a user `me` with a generated password for the User Portal
and a user `admin` with a generated password for the Admin Portal. Those are
printed at the end of the deploy script.

If you want to update/add users you can use the `vpn-user-portal-add-user` and
`vpn-admin-portal-add-user` scripts:

    $ sudo vpn-user-portal-add-user --user john --pass s3cr3t

Or to update the existing `admin` password:

    $ sudo vpn-admin-portal-add-user --user admin --pass 3xtr4s3cr3t

#### LDAP

It is easy to enable LDAP authentication. This is documented separately. See
[LDAP](LDAP.md).

#### SAML

It is easy to enable SAML authentication for identity federations, this is 
documented separately. See [SAML](SAML.md).

### 2FA

For connecting to the VPN service by default only certificates are used, no 
additional user name/password authentication. It is possible to enable 
[2FA](2FA.md) to require an additional TOTP or YubiKey.

### ACLs

If you want to restrict the use of the VPN a bit more than on whether someone
has an account or not, e.g. to limit certain profiles to certain (groups of)
users, see [ACL](ACL.md).

## Optional

### Let's Encrypt

Run the script (as root):

    $ sudo -s
    # ./lets_encrypt.sh

Make sure you use the exact same DNS name you used when running `deploy.sh`! 

After completing the script, the certificate will be installed and the system 
will automatically replace the certificate before it expires.

### Modern PHP

You can switch to modern PHP for performance (and security) reasons:

**NOTE**: this is experimental. This PHP version is not supported by CentOS and
depends on [Remi's RPM repository](https://blog.remirepo.net/).

    $ sudo -s
    # ./switch_to_remi_php.sh
