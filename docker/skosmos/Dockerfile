# ---------------------------------------------------------------------------
# Stage 1
FROM php:7.4-apache AS builder

# 458 MB

WORKDIR /app/

RUN apt-get update && apt-get -y install git unzip libxml2-dev libxslt1-dev

# 495MB

RUN docker-php-ext-install gettext xsl intl

# 495MB

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# 497 MB

RUN composer global require hirak/prestissimo

# Checkout the site
RUN git clone --depth 1 https://github.com/NatLibFi/Skosmos.git /app

# 543 MB

RUN composer install --no-interaction --no-scripts --no-dev

# NOTE: Skipping --prefer-source saved 200 MB+, because we don't get all
# the .git folders inside vendor!!

RUN rm -rf tests tools .git

# ---------------------------------------------------------------------------
# Stage 2
FROM php:7.4-apache

WORKDIR /app

RUN apt-get update && \
    apt-get -y install locales libxml2-dev libxslt1-dev && \
    sed -i 's/^# *\(en_GB.UTF-8\|en_US.UTF-8\|fi_NO.UTF-8\|nb_NO.UTF-8\|nn_NO.UTF-8\|sv_SE.UTF-8\)/\1/' /etc/locale.gen && \
    locale-gen

ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

RUN docker-php-ext-install gettext xsl intl

RUN docker-php-ext-configure opcache --enable-opcache \
    && docker-php-ext-install opcache

# Use the default production configuration
RUN cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

# Override with custom opcache settings
COPY conf/opcache.ini "$PHP_INI_DIR/conf.d/"

# Disable Apache mods we don't need, enable mods we need
RUN a2dismod -f authn* autoindex reqtimeout filter status alias
RUN a2enmod rewrite

COPY --from=builder /app/ /app
COPY test.php /app/

# 505 MB

COPY vhost.conf /etc/apache2/sites-available/000-default.conf

# PHP settings
RUN sed -i "s/;date.timezone =.*/date.timezone = UTC/" $PHP_INI_DIR/php.ini \
	&& sed -i "s/display_startup_errors = Off/display_startup_errors = On/" $PHP_INI_DIR/php.ini \
	&& sed -i "s/display_errors = Off/display_errors = On/" $PHP_INI_DIR/php.ini \
	&& sed -i "s/memory_limit = 128M/memory_limit = 348M/" $PHP_INI_DIR/php.ini \
	&& sed -i "s/file_uploads = On/file_uploads = Off/" $PHP_INI_DIR/php.ini

COPY conf/left.inc conf/footer.inc conf/about.inc /app/view/
COPY conf/config.ttl /app/
