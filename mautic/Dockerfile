FROM mautic/mautic:5.1.1-apache

RUN   echo "SetEnvIf X-Forwarded-Proto \"https\" HTTPS=on" >> /var/www/html/docroot/.htaccess
COPY themes/ /var/www/html/app/themes/