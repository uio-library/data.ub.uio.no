# phusion/baseimage is based on Ubuntu 14.04 LTS
FROM phusion/baseimage:0.9.17

ENV DEBIAN_FRONTEND noninteractive
EXPOSE 80
VOLUME ["/var/log/apache2", "/var/www", "/etc/apache2/sites-available/"]

# Use a nearby mirror
RUN sed -i 's/us.archive.ubuntu.com/ftp.uninett.no/' /etc/apt/sources.list \
  && sed -i 's/archive.ubuntu.com/ftp.uninett.no/' /etc/apt/sources.list \
  && sed -i 's/security.ubuntu.com/ftp.uninett.no/' /etc/apt/sources.list

RUN apt-get update && apt-get -y install \
  apache2 \
  curl \
  gettext \
  libapache2-mod-php5 \
  php-apc \
  php5-cli \
  php5-curl \
  php5-mcrypt \
  php5-xsl

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Enable apache mods.
RUN a2enmod php5 \
 && a2enmod rewrite \
 && a2enmod proxy \
 && a2enmod proxy_http \
 && a2enmod proxy_html

# Examples of how we can modify PHP.ini file:
# RUN sed -i "s/short_open_tag = Off/short_open_tag = On/" /etc/php5/apache2/php.ini
RUN sed -i "s/error_reporting = .*$/error_reporting = E_ALL/" /etc/php5/apache2/php.ini
RUN sed -i "s/display_errors = Off$/display_errors = On/" /etc/php5/apache2/php.ini

# Allow override (.htaccess)
RUN sed -i "s/AllowOverride None/AllowOverride All/g" /etc/apache2/apache2.conf

# Manually set up the apache environment variables
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid

COPY apache.sh /opt/apache.sh
RUN chmod +x /opt/apache.sh

# Update the default apache site with the config we created.
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
COPY 001-fuseki.conf /etc/apache2/sites-available/001-fuseki.conf
COPY 002-skosmos.conf /etc/apache2/sites-available/002-skosmos.conf
COPY 003-yasqe.conf /etc/apache2/sites-available/003-yasqe.conf

RUN a2ensite 001-fuseki.conf
RUN a2ensite 002-skosmos.conf
RUN a2ensite 003-yasqe.conf

# RUN service apache2 reload

# RUN chown -R www-data:www-data /var/www/site
# RUN chown -R www-data:www-data /var/log/apache2

# By default, simply start apache.

WORKDIR "/opt"
CMD "./apache.sh"
