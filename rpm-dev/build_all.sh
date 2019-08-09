#!/bin/sh
for i in *.spec
do
	BN=$(basename $i .spec)
	./local_build.sh ${BN} && ./copr_build.sh ${BN} &
done
