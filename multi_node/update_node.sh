#!/bin/sh

sudo yum clean expire-cache && sudo yum -y update
sudo vpn-server-node-server-config
