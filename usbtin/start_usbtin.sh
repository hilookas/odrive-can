#!/bin/bash

# configure usbtin can interface
sudo modprobe can
sudo modprobe can-raw
sudo modprobe slcan

sudo slcan_attach -f -s5 -o /dev/ttyACM0
sudo slcand ttyACM0 slcan0
sudo ifconfig slcan0 up
