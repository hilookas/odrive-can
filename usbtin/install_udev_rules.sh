#!/bin/bash

# Script to create a udev rule for a specific USB device and create a symlink named "usbtin"

# Define the udev rule content
udev_rule='SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="000a", SYMLINK+="usbtin"'

# remove existing udev rule
sudo rm -f /etc/udev/rules.d/99-usbtin.rules

# Write the udev rule to a new file in the udev rules directory
echo "$udev_rule" | sudo tee /etc/udev/rules.d/99-usbtin.rules > /dev/null

# Reload udev rules and trigger them
sudo udevadm control --reload-rules && sudo udevadm trigger

echo "Udev rule for USB device (idVendor=04d8, idProduct=000a) installed. Symlink 'usbtin' created."
