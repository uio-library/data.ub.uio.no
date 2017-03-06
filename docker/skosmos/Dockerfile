# phusion/baseimage is based on Ubuntu 14.04 LTS
FROM phusion/baseimage:0.9.18

ENV DEBIAN_FRONTEND noninteractive

# Ensure UTF-8
RUN locale-gen en_US.UTF-8 \
  nb_NO.UTF-8 \
  nn_NO.UTF-8 \
  fi_FI.UTF-8 \
  sv_SE.UTF-8
ENV LANG       en_US.UTF-8
ENV LC_ALL     en_US.UTF-8

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# Apt magic
RUN echo 'APT::Install-Recommends "0"; \n\
    APT::Get::Assume-Yes "true"; \n\
    APT::Get::force-yes "true"; \n\
    APT::Install-Suggests "0";' \
    > /etc/apt/apt.conf.d/01buildconfig \
  && echo " \
    deb mirror://mirrors.ubuntu.com/mirrors.txt trusty main restricted universe multiverse \n\
    deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-updates main restricted universe multiverse \n\
    deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-backports main restricted universe multiverse \n\
    deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-security main  restricted universe multiverse \n\
    " \
    > /etc/apt/sources.list

# RUN /etc/my_init.d/00_regen_ssh_host_keys.sh

# Nginx-PHP Installation
RUN apt-get update && apt-get install -y vim \
  curl \
  wget \
  build-essential \
  git \
  python-software-properties

RUN add-apt-repository -y ppa:ondrej/php \
  && apt-get update \
  && apt-get install -y --force-yes \
    php5-cli \
    php5-fpm \
    php5-curl

RUN add-apt-repository -y ppa:nginx/stable \
  && apt-get update \
  && apt-get install -y nginx

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=bin --filename=composer

# The site itself
RUN mkdir -p        /var/www
RUN git clone https://github.com/NatLibFi/Skosmos /var/www/skosmos \
  && cd /var/www/skosmos \
  && git checkout -b v1.8 \
  && composer install --prefer-source --no-interaction


# Daemons to be run by runit
ADD build/nginx.sh  /etc/service/nginx/run
RUN chmod +x        /etc/service/nginx/run
ADD build/phpfpm.sh /etc/service/phpfpm/run
RUN chmod +x        /etc/service/phpfpm/run

# PHP settings
RUN sed -i "s/;date.timezone =.*/date.timezone = UTC/" /etc/php5/fpm/php.ini
RUN sed -i "s/;date.timezone =.*/date.timezone = UTC/" /etc/php5/cli/php.ini

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN sed -i -e "s/;daemonize\s*=\s*yes/daemonize = no/g" /etc/php5/fpm/php-fpm.conf
# RUN sed -i "s/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/" /etc/php5/fpm/php.ini

RUN sed -i "s/display_startup_errors = Off/display_startup_errors = On/" /etc/php5/fpm/php.ini
RUN sed -i "s/display_errors = Off/display_errors = On/" /etc/php5/fpm/php.ini
RUN sed -i "s/memory_limit = 128M/memory_limit = 348M/" /etc/php5/fpm/php.ini
RUN sed -i "s/file_uploads = On/file_uploads = Off/" /etc/php5/fpm/php.ini

RUN sed -i "s/;php_admin_value\[error_log\]/php_admin_value\[error_log\]/" /etc/php5/fpm/pool.d/www.conf
RUN sed -i "s/;php_admin_flag\[log_errors\]/php_admin_flag\[log_errors\]/" /etc/php5/fpm/pool.d/www.conf
RUN sed -i "s/;catch_workers_output = yes/catch_workers_output = yes/" /etc/php5/fpm/pool.d/www.conf

ADD conf/left.inc /var/www/skosmos/view/left.inc
ADD conf/footer.inc /var/www/skosmos/view/footer.inc
ADD conf/about.inc /var/www/skosmos/view/about.inc
ADD conf/config.inc /var/www/skosmos/config.inc
ADD conf/vocabularies.ttl /var/www/skosmos/vocabularies.ttl

ADD build/nginx.php.conf   /etc/nginx/php.conf
ADD build/nginx.site.conf   /etc/nginx/sites-available/default

EXPOSE 80
# VOLUME /var/www/skosmos

# Clean up when done
RUN apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
