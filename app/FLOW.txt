1. show list of profiles for configured VPN providers

2. user chooses an existing VPN provider profile, or chooses "new"
   "new":
     * show a list of available VPN providers
     * user chooses a VPN provider
   "existing":
     * --> 3

2A: obtain the "info.json" of the provider to figure out all the endpoints

3. do we have a non-expired access_token for this provider?
   "no": 
      do we have a refresh_token for this provider?
      "yes":
         attempt to use refresh_token to obtain new access_token
         "error": 
            * delete refresh_token and access_token
            * --> 4
         "ok": 
            * --> 5
      "no":
        * delete access_token (if it is stored)
        * --> 4
   "yes":
      * --> 5

4. obtain a new access_token, authorization_code profile
   * open browser to authorization_endpoint
   * wait for callback
   * exchange authoriztion_code for access_token
   * store access_token (and optionally refresh_token)
   * --> 5

5. fetch system messages and user messages
   "token error":
      * delete access_token
      * --> 3
  
6. display system and user messages to user

7. did the user request a new profile, i.e. chose new in 2?
   "yes":
      * fetch available profiles
      * allow user to choose a profile
   "no":
      * the user selected an existing provider|profile, use this
      * --> 8

8. do we have a valid (non expired) certificate for this provider?
   "yes":
      * --> 9
   "no":
      * obtain certificate for this profile, store the cert and private key
      * --> 9

9. obtain profile configuration for this provider|profile

10. does this profile require 2FA? 
   "yes":
       * ask for 2FA credential
       * --> 11
   "no":
       * --> 11

11. attempt to connect
    "success?"
       "yes":
           * display IP address and usage statistics
       "no":
           * if it is possible to resolve the error directly do so, if not, 
             show to the user


Possible errors in step 11:
* expired CA
* expired server cert
* expired client/user cert
* blocked user
* 2FA token error
* server offline

Depending on the particular error, actions need to be taken

All OAuth errors (bearer token errors) need to be dealt with, it is only once 
explicitly shown in step 5 how to deal with that

There will probably be still many edge cases not covered here... 
  
