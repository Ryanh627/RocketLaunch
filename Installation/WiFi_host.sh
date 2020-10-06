#!/bin/bash

sudo apt install hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo apt install dnsmasq
sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent
sudo mv /etc/dhcpcd.conf /etc/dhcpcdOld.conf
sudo cp /home/pi/RocketLaunch/Installation/WiFi_host_files/dhcpcd.conf /etc/dhcpcd.conf
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo cp /home/pi/RocketLaunch/Installation/WiFi_host_files/dnsmasq.conf /etc/dnsmasq.conf
sudo rfkill unblock wlan
sudo cp //home/pi/RocketLaunch/Installation/WiFi_host_files/hostapd.conf /etc/hostapd/hostapd.conf
sudo systemctl reboot