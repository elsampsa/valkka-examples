#!/bin/bash
sudo rm -f /var/lib/dhcp/dhcpd.leases
sudo touch /var/lib/dhcp/dhcpd.leases
sudo cp dhcpd.conf /etc/dhcp/dhcpd.conf
sudo dhcpd -f
