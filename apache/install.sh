#!/bin/bash

yum -y install httpd mod_wsgi mod_ssl

\cp data_ub_uio_no.conf /etc/httpd/conf.d/data_ub_uio_no.conf
\cp ssl.conf /etc/httpd/conf.d/ssl.conf
\cp status.conf /etc/httpd/conf.d/status.conf
\cp 01-deflate.conf /etc/httpd/conf.modules.d/01-deflate.conf

mkdir -p /etc/httpd/includes
\cp data_ub_uio_no /etc/httpd/includes/data_ub_uio_no


sed -i 's|DocumentRoot "/var/www/html"|DocumentRoot "/opt/data.ub/www/default"|' /etc/httpd/conf/httpd.conf
sed -i 's|<Directory "/var/www">|<Directory "/opt/data.ub/www">|' /etc/httpd/conf/httpd.conf
sed -i 's|<Directory "/var/www/html">|<Directory "/opt/data.ub/www/default">|' /etc/httpd/conf/httpd.conf
