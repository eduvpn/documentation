#!/bin/sh
php-json-signer --sign --name production institute_access.json secure_internet.json
php-json-signer --sign --name development institute_access_dev.json secure_internet_dev.json
php-json-signer --sign --name development_v2 secure_internet_dev_v2.json
