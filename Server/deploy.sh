#!/bin/bash

# software setup
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install -y python3 python3-pip apache2 libapache2-mod-wsgi-py3
mkvirtualenv sr04_server --python=python3

# Project repo setup
git clone https://gitlab.utc.fr/divitare/CryptMyCloud.git
rm -rf CryptMyCloud/PythonClient/
mv CryptMyCloud/Server/* CryptMyCloud/
rm -rf CryptMyCloud/Server/
cd CryptMyCloud

# Django setup
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic

# Database setup
sudo chmod g+w db.sqlite3
sudo chown :www-data db.sqlite3

sudo chmod g+w ../CryptMyCloud
sudo chown :www-data ../CryptMyCloud

# Apache setup
sudo cat > /etc/apache2/sites-available/000-default.conf <<EOL
<VirtualHost *:80>
    ServerAdmin admin@example.com

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

    # This is optional, in case you want to redirect people
    # from http to https automatically.
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule (.*) https://%{SERVER_ADDR}/%{REQUEST_URI}

</VirtualHost>
EOL

sudo mkdir /etc/apache2/certs
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/apache2/certs/cryptmycloud.key -out /etc/apache2/certs/cryptmycloud.crt

cat > /etc/apache2/sites-available/default-ssl.conf <<EOL
<VirtualHost *:443>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        SSLEngine on
        SSLCertificateFile /etc/apache2/certs/cryptmycloud.crt
        SSLCertificateKeyFile /etc/apache2/certs/cryptmycloud.key

        <Directory /home/pi/CryptMyCloud/server>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

        Alias /static/ /home/pi/CryptMyCloud/static/

        <Directory /home/pi/CryptMyCloud/static>
                Options Indexes FollowSymLinks
                AllowOverride None
                Require all granted
        </Directory>

        WSGIDaemonProcess CryptMyCloud python-home=/home/pi/.virtualenvs/sr04_server/ python-path=/home/pi/CryptMyCloud
        WSGIProcessGroup CryptMyCloud
        WSGIScriptAlias / /home/pi/CryptMyCloud/server/wsgi.py
        WSGIPassAuthorization On
</VirtualHost>
EOL

a2ensite default-ssl
a2enmod rewrite  # redirection
a2enmod ssl  # ssl

sudo service apache2 restart  # restart apache

# source /etc/apache2/envvars
