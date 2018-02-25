#!/bin/sh
php-json-signer --sign --name production institute_access.json secure_internet.json
php-json-signer --sign --name development institute_access_dev.json secure_internet_dev.json
