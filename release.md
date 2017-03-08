# Release

This is the software that is packaged for the release of eduVPN. It contains 
all dependencies that are not (yet) packaged for EPEL.

| Component                            | GitHub                           | Git Hash                                 | Version |
| ------------------------------------ | -------------------------------- | ---------------------------------------- | ------- |
| php-bacon-bacon-qr-code              | Bacon/BaconQrCode                | 031a2ce68c5794064b49d11775b2daf45c96e21c | 1.0.1   |
| php-christian-riesen-base32          | ChristianRiesen/base32           | 0a31e50c0fa9b1692d077c86ac188eecdcbaf7fa | 1.3.1   |
| php-christian-riesen-otp             | ChristianRiesen/otp              | 83f941e1ad6f7a2ff318e30cbf5b3219e63a9a62 | 2.3.0   |
| php-paragonie-constant-time-encoding | paragonie/constant_time_encoding | d96e63b79a7135a65659ba5b1cb02826172bfedd | 1.0.1   |
| php-fkooman-oauth2-client            | fkooman/php-oauth2-client        | 73522366282c2ffb4ea89efbf5a2e51b247b8618 | 5.0.0   |
| php-fkooman-oauth2-server            | fkooman/php-oauth2-server        | 11c6cd938250c0a1579ea0b2d589e58ea1ff9c69 | 0.1.0   |
| php-fkooman-yubitwee                 | fkooman/php-yubitwee             | 210072bc79f44ccad36784220b42de3eb07358d3 | 0.1.0   |
| vpn-lib-common                       | eduVPN/vpn-lib-common            | ee497fc26e20141aefbc639dae7822b93a4a631f | 1.0.0   |
| vpn-admin-portal                     | eduVPN/vpn-admin-portal          | 4108dbc9fd76ecb4f07a8ad9c22e8639c3af7cdf | 1.0.0   |
| vpn-server-api                       | eduVPN/vpn-server-api            | b033bc06c80da189b4bab6a946d44a4a3177a955 | 1.0.0   |
| vpn-server-node                      | eduVPN/vpn-server-node           | 1eeea38bb9d7bfacd01d017bd7fae353cfc82f45 | 1.0.0   |
| vpn-user-portal                      | eduVPN/vpn-user-portal           | 4c2a0f7aedeed6ba2405bdd8bcb14997b6fc6c94 | 1.0.0   |

## Preparation

We assuming you work on a fresh CentOS 7 machine:

Install the dependencies:

    $ sudo yum -y install epel-release
    $ sudo yum -y install fedora-packager

Get the RPM spec files:

    $ git clone https://github.com/eduVPN/specs.git

## Getting Tarballs

    $ curl -O -L https://github.com/<GitHub>/archive/<Git Hash>/<GitHub After Slash>-<Version>-<Git Hash>.tar.gz

For example:

    $ curl -O -L https://github.com/Bacon/BaconQrCode/archive/031a2ce68c5794064b49d11775b2daf45c96e21c/BaconQrCode-1.0.1-031a2ce68c5794064b49d11775b2daf45c96e21c.tar.gz

## Generating SRPM

If you just want to build the (S)RPM package, you get the accompanying `spec` 
file from the `eduVPN/specs` repository.

Copy the source to the right location:

    $ rpmdev-setuptree
    $ cp BaconQrCode-1.0.1-031a2ce68c5794064b49d11775b2daf45c96e21c.tar.gz $HOME/rpmbuild/SOURCES
    $ cp specs/php-bacon-bacon-qr-code.spec $HOME/rpmbuild/SPECS

If there are any other files that start with `php-bacon-bacon-qr-code` in the 
`specs/` folder, copy them to `SOURCES`.

Create the SRPM:

    $ cd $HOME/rpmbuild/SPECS
    $ rpmbuild -bs php-bacon-bacon-qr-code.spec

With the SRPMs, you can now use the Docker builder to actually create the RPMs.
