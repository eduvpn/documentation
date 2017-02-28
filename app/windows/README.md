# 1. Introduction
Some information (such as the motives behind these apps and their benefits) are already outlined in the Android functional requirements, as of such they will not be repeated here. This document will consist of:

* Functional requirements
* Application flow
* Application design

# 2. Functional requirements
The functional requirements describe *what* the application must be capable of and not necessarily *how*. The [Application flow](https://github.com/eduvpn/documentation/blob/master/app/APP_FLOW.md) will provide an in depth view on how the application should work.

## Supported operating systems
The application *must* be compatible with Micrsoft's Windows Desktop and Phone 8.1 and higher. Windows 7 is also still being used by our institutions, but developing the eduVPN application for Windows 7 proves to be more troublesome because of Win32. We will start with UWP.

## Authorization
Each eduVPN or Let's Connect! instance can configure their own authentication method. It could be a simple username and password, ir be integrated in a SAML federation like SURFconext. This is of no consequence to the app since it will only use OAuth 2.0 tokens to interact with the instance.

The OAuth flow is explained in more details in the [Application flow](https://github.com/eduvpn/documentation/blob/master/app/APP_FLOW.md).

## Development
* *Principe 1*: Anyone with a computer with just Microsoft Visual Basic Community *must* be able to build the application and its dependencies from source in the easiest way possible and generate an installable application (exe).
* All used components (core, dependencies etc.) in the application *must* be free software.
* In contrary to the Android application (where everything *must* be build from source) the OpenVPN 2.4 binary *may* be provided with the eduVPN application.
* In case additional dependencies are required, they *must* be clearly mentioned in the main README, *must* be free software and *must* have compatible licensing.
* The official OpenVPN for Windows application *must* be used. This is free software and can be integrated directly in the eduVPN application (through binary or from source, see the fourth bullet).

## Publishing
eduVPN will be made available on the eduVPN website (executable) and the Windows Store.

* The application *must* be compatible with the Windows Store and its guidelines.
* The application *must* be automatically updated when the Windows Store variant is chosen by the user.
* The application can be updated with preservation of the added profiles when the user downloads the exe and installs the new version of the app. 

## Additional requirements
* The downloaded VPN configuration and/or other secrets *must* be only stored in protected storage that is only available to the eduvpn application.
* It *must* be possible to manually specify an instance by its URL (in case it is not listed in instances.json).
* Administrator privileges *must not* be required at runtime (after installation has been completed).
* The license *must* be compatible with OpenVPN for Windows and / or other used components. An exact license needs to be determined, but initially the GPLv3 (or later) *must* be used.
* The eduVPN project within the [Commons Conservancy](https://commonsconservancy.org/) receives a worldwide, royalty-free, perpetual and irrevocable license with the right to transfer an unlimited number of non-exclusive licenses or to grant sublicenses to third parties under the Copyright covering the Contribution to use the Contribution by all means.

# 3. Application flow
The [application flow](https://github.com/eduvpn/documentation/blob/master/app/APP_FLOW.md) describes how the application should work with the API and provides an overview of all the steps within the application.

# 4. Application design
The application design describes the interface, design choices, looks and the user experience.

## Design
The design is based on other Windows Universal Apps that had some similarities with our Android application. Although the app looks a lot like the Android app, some elements are quite different. A few examples:

* There is a three button menu in the top of the application.
* The Connection tab consists of one page with notifications and and connection info.
* There is a dedicated back button left to the tab title.
* There is no footer, and thus no SURFnet logo.
* The Segoe UI font is used for all text.

## Control and manage
The application resides in the icon tray on the user's taskbar. When not connected, the normal eduVPN logo will be the app icon. When connected the icon turns green, as shown on the screenshot below.

When clicked with a single or double left mouse button, the UI will show above the icon (as shown in the screenshot). When the cross in the right top of the UI is clicked, the eduVPN will return to the icon tray closing the UI but not the VPN-connection or application itself. To really exit eduVPN, one must right click the icon and click "Exit".

![alt text](https://raw.githubusercontent.com/eduvpn/documentation/master/app/windows/4-wallpaper-desktop.jpg "Screenshot eduVPN Windows application")

## User flow
The primary user flow (of the most important parts of the UI) is listed in the picture below. Note that there are no mockups for the settings tab and the view log window, these should be created in line with this design and the operating system (just like we did on Android).

![alt text](https://raw.githubusercontent.com/eduvpn/documentation/master/app/windows/5-user-flow.png "User flow")

# 5. Things to think about
* On Android, users download the app through the Play Store of F-Droid. Both will alert the user when updates are available, but this will not be the case on Windows since a lot of users don't user the Windows Store (and with good reason). How can we alert users that their app needs an update? Are there UWP native methods for this?

# 6. References
* [OpenVPN (GUI) 2.4.X](https://openvpn.net/index.php/open-source/downloads.html)
* [Previous Android version of these docs](https://github.com/eduvpn/documentation/tree/master/app/android)
