#!/bin/bash

\cp 000-default.conf /etc/httpd/conf.d/000-default.conf
\cp 01-deflate.conf /etc/httpd/conf.modules.d/01-deflate.conf

sed -i 's|DocumentRoot "/var/www/html"|DocumentRoot "/opt/data.ub/www/default"|' /etc/httpd/conf/httpd.conf
sed -i 's|<Directory "/var/www">|<Directory "/opt/data.ub/www">|' /etc/httpd/conf/httpd.conf
sed -i 's|<Directory "/var/www/html">|<Directory "/opt/data.ub/www/default">|' /etc/httpd/conf/httpd.conf
