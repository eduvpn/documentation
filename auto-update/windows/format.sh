#!/bin/sh

for i in *.json
do
	cat "${i}" | python -mjson.tool > tmp
        mv tmp "${i}"
done
