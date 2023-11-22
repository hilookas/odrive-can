#!/bin/bash

# see https://www.waveshare.com/wiki/2-CH_CAN_HAT#Enable_SPI_interface


set -e
set -x

wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
tar zxvf bcm2835-1.60.tar.gz
cd bcm2835-1.60/
sudo ./configure
sudo make
sudo make check
sudo make install
