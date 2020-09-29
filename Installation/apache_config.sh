#!/bin/bash

sudo apt-get update
sudo apt-get install apache2
sudo apt-get install apache2-dev
sudo apt install libapache2-mod-wsgi-py3 -y
sudo cp ../Dependencies/rocketlaunch.conf /etc/apache2/sites-available
sudo a2ensite rocketlaunch.conf
sudo a2dissite 000-default.conf
sudo service apache2 restart
