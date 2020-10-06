#!/bin/bash

sudo rm /etc/dhcpcd.conf
sudo rm /etc/dnsmasq.conf
sudo rm /etc/hostapd/hostapd.conf
sudo service dnsmasq stop
sudo apt remove dnsmasq -y
sudo systemctl reboot