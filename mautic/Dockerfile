FROM mautic/mautic:6.0.5-apache

RUN   echo "SetEnvIf X-Forwarded-Proto \"https\" HTTPS=on" >> /var/www/html/docroot/.htaccess
COPY --chown=www-data:www-data themes/. /var/www/html/docroot/themes