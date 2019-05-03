---
title: User Delete
description: Manually fully Delete a User
category: howto
---

This document describes how to delete a user from the VPN server. Note: 
depending on the user authentication method there may be more to delete.

User data is stored in two locations:

1. The vpn-user-portal (OAuth tokens for use by API)
2. The vpn-server-api (2FA, certificate mapping, logging)

# User Portal

If you are using the *default* username/password authentication you need to 
delete the user from the user database. This is *NOT* relevant for SAML, LDAP 
and RADIUS authentication:

```bash
$ sudo sqlite3 /var/lib/vpn-user-portal/db.sqlite
SQLite version 3.7.17 2013-05-20 00:56:22
Enter ".help" for instructions
Enter SQL statements terminated with a ";"
sqlite> DELETE FROM users WHERE user_id = 'demo';
sqlite> .q
```

Delete the OAuth tokens for the user, relevant for all authentication backends:

```bash
$ sudo sqlite3 /var/lib/vpn-user-portal/db.sqlite
SQLite version 3.7.17 2013-05-20 00:56:22
Enter ".help" for instructions
Enter SQL statements terminated with a ";"
sqlite> DELETE FROM authorizations WHERE user_id = 'ABCD';
sqlite> .q
```

# Server API

Make sure to enable "foreign keys" with the `PRAGMA` statement shown below, 
this is to delete the user data from all other tables that have a foreign key
associated with the user in the users table.

```bash
$ sudo sqlite3 /var/lib/vpn-server-api/db.sqlite
SQLite version 3.7.17 2013-05-20 00:56:22
Enter ".help" for instructions
Enter SQL statements terminated with a ";"
sqlite> PRAGMA foreign_keys = ON;
sqlite> DELETE FROM users WHERE user_id = 'ABCD';
sqlite> .q
```

We will not touch the CA, the user will have certificates in the CA as well,
but they are in no way relatable to the user anymore after deleting the user
information as shown above. The certificates use a randomly generated CN.

The logging is NOT deleted using this query. The log will be deleted after 30
days through the "housekeeping" cronjob.
