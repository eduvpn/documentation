# Database Authentication

By default the VPN server has database authentication for user accounts. The 
accounts are stored in the local database.

If you did not set any (other) `authModule` in your 
`/etc/vpn-user-portal/config.php` file, this is what you have.

To configure other ways of user authentication, look 
[here](PORTAL_CONFIG.md#authentication).

## Configuration

There is nothing to configure.

## User Management

You can manage the users using the `vpn-user-portal-account` tool.

### Add User

To add the user `foo`, use the following:

```bash
$ sudo vpn-user-portal-account --add foo
```

You'll be asked to provide the password (twice). After that, the account will
be created. It is also possible to specify the password when creating the user:

```bash
$ sudo vpn-user-portal-account --add foo --password s3cr3t
```

### List Users

You can list the users:

```bash
$ sudo vpn-user-portal-account --list
```

### Delete User

You can delete a user, e.g. to delete the user `foo`:

```bash
$ sudo vpn-user-portal-account --delete foo
```

If you do not want to ask for confirmation before deleting the account, you can 
use the `--force` flag.

### Disable / Enable User

```bash
$ sudo vpn-user-portal-account --disable foo
$ sudo vpn-user-portal-account --enable foo
```
