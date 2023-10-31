#!/bin/bash

# install udev rules for odrive

# Define the udev rules file path
udev_rules_file="/etc/udev/rules.d/91-odrive.rules"

# Check if the udev rules file already exists
if [[ ! -e $udev_rules_file ]]; then
    # The udev rules file does not exist, install the rules
    echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1209", ATTR{idProduct}=="0d[0-9][0-9]", MODE="0666"' | sudo tee $udev_rules_file
    sudo udevadm control --reload-rules
    sudo udevadm trigger
else
    # The udev rules file already exists, notify the user
    echo "The udev rules file $udev_rules_file already exists. No action taken."
fi
