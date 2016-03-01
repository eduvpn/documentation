#!/bin/sh

# instance configuration
API_ID=6492bda3501e39a2
API_SECRET=XXXX
API_URI=https://vpn.tuxed.net/portal/api/config
ROUTER_V6=fd00:4242:4242:4242::1

# test configuration
PREFIX=vpn_

# download the configurations
for i in {1..5}
do
        echo ${i}
#	curl -s -o ${PREFIX}${i}.ovpn -u ${API_ID}:${API_SECRET} -d "name=${PREFIX}${i}" ${API_URI}
done

# start the VPNs
for i in {1..5}
do
	sudo openvpn --config ${PREFIX}${i}.ovpn --daemon --route-nopull
done

# wait for the VPNs to come up
sleep 5

# start the pings, we use ping6
# it seems IPv4 pings do not work over other interfaces?
for i in {0..4}
do
	ping6 -s 32768 ${ROUTER_V6} -I tun${i} >/dev/null 2>/dev/null &
done
