# Introduction

This document describes the OpenVPN AS API as used by the OpenVPN Connect 
client, at least on Android. Perhaps also on iOS.

In the client we use "Import" -> "Import Access Server Profile". For the 
"Access Server Hostname" we used `as.tuxed.net:8443`, for "Username" we used
`foo` and for "Password" we used `bar`. We also selelected 
"Import autologin profile". After that we clicked "Import Profile".

# API

The protocol consists of a number of back and forth messages between the
OpenVPN Connect client and the AS. Below a complete example is shown from 
beginning to end as to help in implementing the AS part of the API.

## Request

The first request is to request a "session". The message looks like this, 
the `Authorization` header contains the Base64 encoded `foo:bar` password.

    POST /RPC2 HTTP/1.1
    Authorization: Basic Zm9vOmJhcg==
    User-Agent: Dalvik/1.6.0 (Linux; U; Android 4.4.4; GT-I9300 Build/KTU84Q)
    Host: as.tuxed.net:8443
    Connection: Keep-Alive
    Accept-Encoding: gzip
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 103

    <?xml version="1.0"?>
    <methodCall>
    <methodName>GetSession</methodName>
    <params></params>
    </methodCall>

## Response

The response consist of a `session_id`. This is an opaque, presumable random 
string of length 16 bytes, Base64 encoded.

    HTTP/1.1 200 OK
    Date: Fri, 05 Feb 2016 09:31:07 GMT
    Content-Length: 294
    Content-Type: text/xml
    Server: OpenVPN-AS

    <?xml version='1.0'?>
    <methodResponse>
    <params>
    <param>
    <value><struct>
    <member>
    <name>status</name>
    <value><int>0</int></value>
    </member>
    <member>
    <name>session_id</name>
    <value><string>2LChXiEy4oK150jraN+4sA==</string></value>
    </member>
    </struct></value>
    </param>
    </params>
    </methodResponse>

## Request

The next request calls for the supported configuration types. The 
`Authorization` header is a little special here: 

    $ echo -n 'U0VTU0lPTl9JRDoyTENoWGlFeTRvSzE1MGpyYU4rNHNBPT0=' | base64 -d
    SESSION_ID:2LChXiEy4oK150jraN+4sA==

So, it again contains the previously obtained `session_id`. So a Base64 encode
of `SESSION_ID:` with the `session_id` appended.

    POST /RPC2 HTTP/1.1
    Authorization: Basic U0VTU0lPTl9JRDoyTENoWGlFeTRvSzE1MGpyYU4rNHNBPT0=
    User-Agent: Dalvik/1.6.0 (Linux; U; Android 4.4.4; GT-I9300 Build/KTU84Q)
    Host: as.tuxed.net:8443
    Connection: Keep-Alive
    Accept-Encoding: gzip
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 108

    <?xml version="1.0"?>
    <methodCall>
    <methodName>EnumConfigTypes</methodName>
    <params></params>
    </methodCall>

## Response

Here is the response, we are mostly interested in the `autologin` configuration
though, maybe the rest can be left out.

    HTTP/1.1 200 OK
    Date: Fri, 05 Feb 2016 09:31:08 GMT
    Content-Length: 1123
    Content-Type: text/xml
    Server: OpenVPN-AS

    <?xml version='1.0'?>
    <methodResponse>
    <params>
    <param>
    <value><struct>
    <member>
    <name>generic</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>userlogin</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>userlocked</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>autologin</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>cws_ui_offer</name>
    <value><struct>
    <member>
    <name>user_locked</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>win</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>ios</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>autologin</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>mac</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>linux</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>android</name>
    <value><boolean>1</boolean></value>
    </member>
    <member>
    <name>server_locked</name>
    <value><boolean>0</boolean></value>
    </member>
    </struct></value>
    </member>
    </struct></value>
    </param>
    </params>
    </methodResponse>

## Request

Now we obtain the actual configuration.

    POST /RPC2 HTTP/1.1
    Authorization: Basic U0VTU0lPTl9JRDoyTENoWGlFeTRvSzE1MGpyYU4rNHNBPT0=
    User-Agent: Dalvik/1.6.0 (Linux; U; Android 4.4.4; GT-I9300 Build/KTU84Q)
    Host: as.tuxed.net:8443
    Connection: Keep-Alive
    Accept-Encoding: gzip
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 105

    <?xml version="1.0"?>
    <methodCall>
    <methodName>GetAutologin</methodName>
    <params></params>
    </methodCall>

## Response

The OpenVPN configuration. It seems some of the variables, part of the 
comments are used by the OpenVPN AS client to display in the UI of the client,
a quick look shows that at least `OVPN_ACCESS_SERVER_PROFILE` and 
`OVPN_ACCESS_SERVER_USERNAME` are visible in the UI.

I am worried about the `## -----BEGIN RSA SIGNATURE-----` in the configuration
that possibly is verified by the client... It will require a lot of work to 
make this work then.

    HTTP/1.1 200 OK
    Date: Fri, 05 Feb 2016 09:31:09 GMT
    Content-Length: 11850
    Content-Type: text/xml
    Server: OpenVPN-AS

    <?xml version='1.0'?>
    <methodResponse>
    <params>
    <param>
    <value><string># Automatically generated OpenVPN client config file
    # Generated on Fri Feb  5 09:31:09 2016 by as.tuxed.net
    # Note: this config file contains inline private keys
    #       and therefore should be kept confidential!
    # Note: this configuration is user-locked to the username below
    # OVPN_ACCESS_SERVER_USERNAME=foo
    # Define the profile name of this particular configuration file
    # OVPN_ACCESS_SERVER_PROFILE=foo@as.tuxed.net/AUTOLOGIN
    # OVPN_ACCESS_SERVER_AUTOLOGIN=1
    # OVPN_ACCESS_SERVER_CLI_PREF_ALLOW_WEB_IMPORT=True
    # OVPN_ACCESS_SERVER_CLI_PREF_ENABLE_CONNECT=True
    # OVPN_ACCESS_SERVER_CLI_PREF_ENABLE_XD_PROXY=True
    # OVPN_ACCESS_SERVER_WSHOST=as.tuxed.net:443
    # OVPN_ACCESS_SERVER_WEB_CA_BUNDLE_START
    # -----BEGIN CERTIFICATE-----
    # XXX
    # -----END CERTIFICATE-----
    # OVPN_ACCESS_SERVER_WEB_CA_BUNDLE_STOP
    # OVPN_ACCESS_SERVER_IS_OPENVPN_WEB_CA=0
    # OVPN_ACCESS_SERVER_ORGANIZATION=OpenVPN Technologies, Inc.
    setenv FORWARD_COMPATIBLE 1
    client
    server-poll-timeout 4
    nobind
    remote as.tuxed.net 1194 udp
    remote as.tuxed.net 1194 udp
    remote as.tuxed.net 443 tcp
    remote as.tuxed.net 1194 udp
    remote as.tuxed.net 1194 udp
    remote as.tuxed.net 1194 udp
    remote as.tuxed.net 1194 udp
    remote as.tuxed.net 1194 udp
    dev tun
    dev-type tun
    ns-cert-type server
    reneg-sec 604800
    sndbuf 100000
    rcvbuf 100000
    # NOTE: LZO commands are pushed by the Access Server at connect time.
    # NOTE: The below line doesn't disable LZO.
    comp-lzo no
    verb 3
    setenv PUSH_PEER_INFO

    &lt;ca&gt;
    -----BEGIN CERTIFICATE-----
    XXX
    -----END CERTIFICATE-----
    &lt;/ca&gt;

    &lt;cert&gt;
    -----BEGIN CERTIFICATE-----
    XXX
    -----END CERTIFICATE-----
    &lt;/cert&gt;

    &lt;key&gt;
    -----BEGIN PRIVATE KEY-----
    XXX
    -----END PRIVATE KEY-----
    &lt;/key&gt;

    key-direction 1
    &lt;tls-auth&gt;
    #
    # 2048 bit OpenVPN static key (Server Agent)
    #
    -----BEGIN OpenVPN Static key V1-----
    XXX
    -----END OpenVPN Static key V1-----
    &lt;/tls-auth&gt;

    ## -----BEGIN RSA SIGNATURE-----
    ## DIGEST:sha256
    ## XXX
    ## -----END RSA SIGNATURE-----
    ## -----BEGIN CERTIFICATE-----
    ## XXX
    ## -----END CERTIFICATE-----
    ## -----BEGIN CERTIFICATE-----
    ## XXX
    ## -----END CERTIFICATE-----
    </string></value>
    </param>
    </params>
    </methodResponse>

## Request

And now closing the session.

    POST /RPC2 HTTP/1.1
    Authorization: Basic U0VTU0lPTl9JRDoyTENoWGlFeTRvSzE1MGpyYU4rNHNBPT0=
    User-Agent: Dalvik/1.6.0 (Linux; U; Android 4.4.4; GT-I9300 Build/KTU84Q)
    Host: as.tuxed.net:8443
    Connection: Keep-Alive
    Accept-Encoding: gzip
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 105

    <?xml version="1.0"?>
    <methodCall>
    <methodName>CloseSession</methodName>
    <params></params>
    </methodCall>

## Response

The response to closing the session.

    <?xml version='1.0'?>
    <methodResponse>
    <params>
    <param>
    <value><nil/></value></param>
    </params>
    </methodResponse>

