#!/bin/sh

sudo systemctl stop httpd
sudo systemctl stop php-fpm
sudo yum clean expire-cache && sudo yum -y update
sudo systemctl start php-fpm
sudo systemctl start httpd
