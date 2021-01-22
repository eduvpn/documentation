# IRMA Authentication

**NOTE**: IRMA authentication is NOT supported, you are on your own!

**NOTE**: The IRMA server is NOT part of the VPN software packages. **YOU** 
are responsible for its installation, configuration, installing updates, 
keep it secure and in general keep it running!

**NOTE**: IRMA authentication is NOT production ready! Check the bottom of this
document for open issues.

## IRMA Server Configuration

First, download the IRMA server according to the documentation from the 
[IRMA documentation](https://irma.app/docs/getting-started/). Then create the 
IRMA configuration file as follows:

```
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
* `url`: The URL on which the server can be found
* `email`: If the email address is specified, you will be subscribed to 
  receives updates about any IRMA software or ecosystem changes. If you do not 
  want the updates, change the line to `no_email: true`
* `disclose_perms`: The attributes the application that uses the specified 
  `key` are allowed to disclose
* `auth_method`: Specifies the authentication method
* `key`: Specifies the key the server has to send in the initial POST-request 
  authentication header in order to be allowed to connect to the server. This 
  token can be whatever you want. It needs to match the token in portal 
  configuration

If you have the IRMA server installed from source, the configuration file must 
be in the `irmago` directory. Furthermore, if you want to start the server, you 
have to change your working directory to `irmago` and start the server with the 
following command:

```
$ go run ./irma server -c irma_configuration_file.yml --production 
```

If you have installed the IRMA server using the prebuilt binary, the 
configuration file has to be placed in the same directory from which you are 
starting the server. Then to start the server, use the following command:

```
$ irma server -c irma_configuration_file.yml --production
```

If you want to add verbosity, you can add the options `-v` or `-vv`.
 
## Portal Configuration

First, install the environment for your OS and follow the instructions from 
the "Base Deploy" and "Web Server Certificates" sections: 
[Fedora](DEPLOY_FEDORA.md), [Debian](DEPLOY_DEBIAN.md), or 
[CentOS](DEPLOY_CENTOS.md).

If you have the environment installed, change the file `config.php` in the 
`/etc/vpn-user-portal/` directory:

First, comment the line 

```
'authMethod' => 'FormPdoAuthentication',        // PDO (database)
```

add the following lines: 

```
'authMethod' => 'IrmaAuthentication',
'IrmaAuthentication' => [
    'irmaServerUrl' => 'https://{your_host_name}/irma/',
    'userIdAttribute' => 'pbdf.sidn-pbdf.email.email',
    'secretToken' => 'mysecrettoken',
],
```

The variables mean the following:

* `authMethod`: The authentication method the VPN service has to use. In our 
  case: IRMA.
* `irmaServerUrl`: The address on which the VPN server can find your IRMA 
  server
* `userIdAttribute`: This is the attribute that the server has to verify
* `secretToken`: This is the token is used to let the server identify itself to 
  the IRMA server

Second, you have to change the Apache configuration file to configure the 
reverse proxy. Change the following file: 
`/etc/httpd/conf.d/{your_host_name}.conf`. You need to add the following 
lines to the HTTPS `VirtualHost`: 

```
ProxyPass 	 "/irma/" "http://localhost:8088/"
ProxyPassReverse "/irma/" "http://localhost:8088/"
```

At last run the following command:

```
$ sudo systemctl restart httpd
```

## Open Issues / TODO

* Do we need `ProxyPassReverse` as well? Or is `ProxyPass` enough?
* Properly package the IRMA server for Debian/Fedora
* Build the `irma.js` file from source, this is simply a "binary" taken from 
  a Gitlab server
* Is the proxy configuration actually safe? Do we need to restrict access in 
  some way? All endpoints are allowed now...
