# IRMA setup
___
### IRMA server
First, download the IRMA server according to the documentation from the [IRMA documentation](https://irma.app/docs/getting-started/).
Then create the IRMA configuration file as follows:
```yml
port: 8088
url: "https://{your_host_name}/irma/irma"
email: "{your email address}"

requestors:
  myapp:
    disclose_perms: [ "pbdf.sidn-pbdf.email.email" ]
    auth_method: "token"
    key: "mysecrettoken"
```
The file can be named as one pleases but has to have the `.yml` extension.

The variables mean the following:
* `port`: The port on which the server can be found
* `url`: The url on which the server can be found
* `email`: If the email address is specified, you will be subscribed to receives updates about any IRMA software or ecosystem changes. If you do not want the updates, change the line to 
```yml
no_email: true
 ```
* `disclose_perms`: The attributes the application that uses the specified `key` are allowed to disclose.
* `auth_method`: Specifies the authentication method. In the case of eduVPN this has to be `token`
* `key`: Specifies the key that the eduVPN server has to send in the initial POST-request authentication header in order to be allowed to connect to the server. This token can be whatever you want. It only needs to match the token in the eduVPN configuration.

If you have the IRMA server installed from source, the configuration file must be in the `irmago` directory. Furthermore, if you want to start the server, you have to change your working directory to `irmago` and start the server with the following command:
```sh
$ go run ./irma server -c irma_configuration_file.yml --production 
```

If you have installed the IRMA server using the prebuilt binary, the configuration file has to be placed in the same directory from which you are starting the server. Then to start the server, use the following command:
```sh
$ irma server -c irma_configuration_file.yml --production
```
 If you want to add verbosity, you can add the options `-v` or `-vv`.
 
### eduVPN configuration
In order to use this environment u need to have a DNS server installed on your machine.

First, install the environment for your OS and follow the instructions from the "Base Deploy" and "Web Server Certificates" sections:  [Fedora](https://github.com/eduvpn/documentation/blob/v2/DEPLOY_FEDORA.md), [Debian](https://github.com/eduvpn/documentation/blob/v2/DEPLOY_DEBIAN.md), or [CentOS](https://github.com/eduvpn/documentation/blob/v2/DEPLOY_CENTOS.md).

If you have the environment installed, change the file `config.php` in the  `/etc/vpn-user-portal/` directory:
First, comment the line 
```php
'authMethod' => 'FormPdoAuthentication',        // PDO (database)
```
add the following lines: 
```php
'authMethod' => 'IrmaAuthentication',
'IrmaAuthentication' => [
    'irmaServerUrl' => 'https://{your_host_name}/irma/',
    'userIdAttribute' => 'pbdf.sidn-pbdf.email.email',
    'secretToken' => 'mysecrettoken',
],
```
The variables mean the following:
   * `authMethod`: The authentication method the VPN service has to use. In our case: IRMA.
   * `irmaServerUrl`: The address on which the VPN server can find your IRMA server
   * `userIdAttribute`: This is the attribute that the server has to verify
   * `secretToken`: This is the token is used to let the server identify itself to the IRMA server

Second, you have to change the Apache configuration file to configure the reverse proxy. Change the following file: `/etc/httpd/conf.d/{your_host_name}.conf`. You need to add the following lines to both of the `VirtualHost` sections: 
```sh
ProxyPass "/irma/"  "http://localhost:8088/"
        ProxyPassReverse "/irma/" "http://localhost:8088/"
```

At last run the following command:
```
$ sudo systemctl restart httpd
```


