# Windows
This page will describe how to configure Windows with OpenVPN. We will focus 
on the official OpenVPN client for Windows. It can be downloaded 
[here](https://openvpn.net/index.php/open-source/downloads.html).

Excellent instructions on how to install OpenVPN for Windows can
be found [here](https://community.openvpn.net/openvpn/wiki/OpenVPN-GUI).

There are two important things:

1. You need to put the `ovpn` configuration file you download in the folder
`C:\Program Files\OpenVPN\config`;
2. You need to start OpenVPN as *Administrator*. This can be done by right 
clicking the "OpenVPN GUI" and selecting "Run as administrator".

You can make the "Run as administrator" the default by changing the 
compatibility settings:

1. Right click on "OpenVPN GUI";
2. Select the "Compatibility" tab;
3. Check the "Run this program as an administrator" box;
4. Click "Apply";


![Run as Administrator](https://raw.githubusercontent.com/eduVPN/documentation/master/windows/windows_openvpn_run_as_administrator.png)

Now when you double click "OpenVPN GUI" it will start as *Administrator*. You 
can start the VPN connection by right clicking on the OpenVPN tray icon and 
clicking "Connect".

![Connect](https://raw.githubusercontent.com/eduVPN/documentation/master/windows/windows_openvpn_connect.png)
