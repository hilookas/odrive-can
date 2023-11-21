#!/bin/bash

# Wait for the symlink to be established
while [ ! -e /dev/usbtin ]; do
    sleep 1
done

# Configure USBtin CAN interface
sudo modprobe can
sudo modprobe can-raw
sudo modprobe slcan

# Use the symlink for slcan_attach
sudo slcan_attach -f -s5 -o /dev/usbtin
sudo slcand -o -c -f /dev/usbtin slcan0
sudo ifconfig slcan0 up
