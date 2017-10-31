# Deploying on CentOS

For simple one server deployments and tests, we have a deploy script available 
you can run on a fresh CentOS 7 installation. It will configure all components 
and will be ready for use after running!

Additional scripts are available after deployment:

* Use [Let's Encrypt](https://letsencrypt.org/) for automatic web server 
  certificate management;
* Switch to PHP 7.1 (experimental)

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
the deploy script and manually follow the steps.

## Base Deploy

Perform these steps on the host where you want to deploy:

    $ curl -L -O https://github.com/eduvpn/documentation/archive/master.tar.gz
    $ tar -xzf master.tar.gz
    $ cd documentation-master

Modify `deploy.sh` and set the variables at the top of the file to something 
that makes sense for your deployment. Read the comments at the top of the file. 

Run the script (as root):

    $ sudo -s
    # ./deploy.sh

## Let's Encrypt

Modify `lets_encrypt.sh` and set the variables at the top of the file to 
something that makes sense for you. Read the comments at the top of the file. 
Make sure the `WEB_FQDN` variable is the same as the one you used in 
`deploy.sh`.

Run the script (as root):

    $ sudo -s
    # ./lets_encrypt.sh

The system will automatically replace the certificate before it expires.

## PHP 7.1

**NOTE**: this configuration is NOT supported!

You can switch to PHP 7.1 for performance (and security) reasons:

    $ sudo -s
    # ./switch_to_php71.sh
